import csv
import io
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cx_contracts.common.enums import ImportJobState, ImportRowOutcome, Sentiment, Severity
from cx_contracts.import_pkg.csv_v1 import (
    EXACT_CSV_V1_HEADERS,
    TRUSTED_CSV_V1_CONTRACT_VERSION,
    compute_row_checksum,
)
from cx_contracts.import_pkg.import_errors import ImportErrorCode
from cx_db.src.models.tables import (
    ImportJobModel,
    ImportRowModel,
    LocationNodeModel,
    ProjectModel,
    SourceRecordModel,
    TaxonomyIssueModel,
    TaxonomyServiceIssueModel,
    TaxonomyServiceModel,
)


async def validate_import_job(session: AsyncSession, job_id: UUID, file_content_bytes: bytes) -> ImportJobModel:
    """Validate import job CSV file content and update job state & rows."""
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError(f"Import job not found: {job_id}")

    job.state = ImportJobState.VALIDATING
    await session.commit()

    # Step 1: Handle BOM and decode UTF-8
    try:
        content_str = file_content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        job.state = ImportJobState.FAILED
        job.invalid_rows = 1
        await session.commit()
        raise ValueError("Invalid UTF-8 encoding in CSV file")

    if "\0" in content_str:
        job.state = ImportJobState.FAILED
        job.invalid_rows = 1
        await session.commit()
        raise ValueError("File contains null bytes")

    # Step 2: Parse CSV structure and verify headers
    csv_reader = csv.reader(io.StringIO(content_str))
    try:
        header = next(csv_reader)
    except StopIteration:
        job.state = ImportJobState.FAILED
        await session.commit()
        raise ValueError("Empty CSV file")

    if header != EXACT_CSV_V1_HEADERS:
        job.state = ImportJobState.FAILED
        await session.commit()
        raise ValueError(f"Invalid CSV header. Expected {EXACT_CSV_V1_HEADERS}, got {header}")

    # Fetch reference data for validation
    project_result = await session.execute(select(ProjectModel).where(ProjectModel.id == job.project_id))
    project = project_result.scalar_one_or_none()
    project_code = project.code if project else ""

    locations_result = await session.execute(
        select(LocationNodeModel.code).where(LocationNodeModel.project_id == job.project_id)
    )
    valid_location_codes = set(locations_result.scalars().all())

    services_result = await session.execute(select(TaxonomyServiceModel.code, TaxonomyServiceModel.id))
    service_map = {row[0]: row[1] for row in services_result.all()}

    issues_result = await session.execute(select(TaxonomyIssueModel.code, TaxonomyIssueModel.id))
    issue_map = {row[0]: row[1] for row in issues_result.all()}

    service_issue_result = await session.execute(
        select(TaxonomyServiceIssueModel.service_id, TaxonomyServiceIssueModel.issue_id).where(
            TaxonomyServiceIssueModel.active == True
        )
    )
    valid_service_issue_pairs = set(service_issue_result.all())

    # Existing database source references for duplicate check
    existing_refs_result = await session.execute(
        select(SourceRecordModel.source_reference).where(SourceRecordModel.source == "PILOT_CSV_V1")
    )
    db_source_refs = set(existing_refs_result.scalars().all())

    seen_file_source_refs: dict[str, int] = {}
    valid_rows_count = 0
    invalid_rows_count = 0
    duplicate_rows_count = 0
    total_rows_count = 0

    rows_to_insert: list[ImportRowModel] = []

    # Clean up previous rows if re-validating
    await session.execute(
        ImportRowModel.__table__.delete().where(ImportRowModel.import_job_id == job_id)
    )

    for idx, row in enumerate(csv_reader, start=1):
        if not row or all(c.strip() == "" for c in row):
            continue  # ignore terminal empty rows

        total_rows_count += 1
        row_errors: list[dict] = []
        
        if len(row) != len(EXACT_CSV_V1_HEADERS):
            row_errors.append({
                "row_number": idx,
                "column": None,
                "code": ImportErrorCode.INVALID_CSV_SYNTAX,
                "message": f"Row has {len(row)} columns, expected {len(EXACT_CSV_V1_HEADERS)}"
            })
            normalized_payload = {}
        else:
            raw_dict = dict(zip(EXACT_CSV_V1_HEADERS, row))
            src_ref = raw_dict["source_reference"].strip()
            rep_at_str = raw_dict["reported_at"].strip()
            proj_code = raw_dict["project_code"].strip()
            loc_code = raw_dict["location_code"].strip()
            srv_code = raw_dict["service_code"].strip()
            iss_code = raw_dict["issue_code"].strip()
            sent_str = raw_dict["sentiment"].strip()
            sev_str = raw_dict["operational_severity"].strip()
            cnt_masked = raw_dict["content_masked"].replace("\r\n", "\n").replace("\r", "\n")

            normalized_payload = {
                "source_reference": src_ref,
                "reported_at": rep_at_str,
                "project_code": proj_code,
                "location_code": loc_code,
                "service_code": srv_code,
                "issue_code": iss_code,
                "sentiment": sent_str,
                "operational_severity": sev_str,
                "content_masked": cnt_masked,
            }

            # 1. Required fields
            if not src_ref:
                row_errors.append({"row_number": idx, "column": "source_reference", "code": ImportErrorCode.REQUIRED_FIELD, "message": "source_reference is required"})
            if not rep_at_str:
                row_errors.append({"row_number": idx, "column": "reported_at", "code": ImportErrorCode.REQUIRED_FIELD, "message": "reported_at is required"})
            if not proj_code:
                row_errors.append({"row_number": idx, "column": "project_code", "code": ImportErrorCode.REQUIRED_FIELD, "message": "project_code is required"})

            # 2. Length limits
            if len(src_ref) > 255:
                row_errors.append({"row_number": idx, "column": "source_reference", "code": ImportErrorCode.VALUE_TOO_LONG, "message": "source_reference exceeds 255 chars"})
            if len(cnt_masked) > 4000:
                row_errors.append({"row_number": idx, "column": "content_masked", "code": ImportErrorCode.VALUE_TOO_LONG, "message": "content_masked exceeds 4000 chars"})

            # 3. Timestamp parsing
            if rep_at_str:
                try:
                    parsed_dt = datetime.fromisoformat(rep_at_str)
                    if parsed_dt.tzinfo is None:
                        row_errors.append({"row_number": idx, "column": "reported_at", "code": ImportErrorCode.INVALID_TIMESTAMP, "message": "reported_at must include timezone offset"})
                except ValueError:
                    row_errors.append({"row_number": idx, "column": "reported_at", "code": ImportErrorCode.INVALID_TIMESTAMP, "message": "reported_at is not valid ISO timestamp"})

            # 4. Project match
            if proj_code and proj_code != project_code:
                row_errors.append({"row_number": idx, "column": "project_code", "code": ImportErrorCode.PROJECT_SCOPE_MISMATCH, "message": f"project_code '{proj_code}' does not match job project '{project_code}'"})

            # 5. Location check
            if loc_code and valid_location_codes and loc_code not in valid_location_codes:
                row_errors.append({"row_number": idx, "column": "location_code", "code": ImportErrorCode.UNKNOWN_LOCATION, "message": f"Unknown location_code '{loc_code}'"})

            # 6. Service / Issue check
            srv_id = service_map.get(srv_code)
            if srv_code and not srv_id:
                row_errors.append({"row_number": idx, "column": "service_code", "code": ImportErrorCode.UNKNOWN_SERVICE, "message": f"Unknown service_code '{srv_code}'"})

            iss_id = issue_map.get(iss_code)
            if iss_code and not iss_id:
                row_errors.append({"row_number": idx, "column": "issue_code", "code": ImportErrorCode.UNKNOWN_ISSUE, "message": f"Unknown issue_code '{iss_code}'"})

            if srv_id and iss_id and valid_service_issue_pairs and (srv_id, iss_id) not in valid_service_issue_pairs:
                row_errors.append({"row_number": idx, "column": "service_code", "code": ImportErrorCode.INVALID_SERVICE_ISSUE, "message": f"Invalid service-issue pair ({srv_code}, {iss_code})"})

            # 7. Sentiment / Severity enums
            if sent_str and sent_str not in Sentiment.__members__:
                row_errors.append({"row_number": idx, "column": "sentiment", "code": ImportErrorCode.INVALID_SENTIMENT, "message": f"Invalid sentiment '{sent_str}'"})

            if sev_str and sev_str not in Severity.__members__ and sev_str not in [s.value for s in Severity]:
                row_errors.append({"row_number": idx, "column": "operational_severity", "code": ImportErrorCode.INVALID_SEVERITY, "message": f"Invalid severity '{sev_str}'"})

        # Determine Outcome
        if row_errors:
            outcome = ImportRowOutcome.INVALID
            invalid_rows_count += 1
        else:
            # Check duplicate in file or DB
            src_ref = normalized_payload.get("source_reference", "")
            if src_ref in seen_file_source_refs:
                outcome = ImportRowOutcome.DUPLICATE
                duplicate_rows_count += 1
                row_errors.append({
                    "row_number": idx,
                    "column": "source_reference",
                    "code": ImportErrorCode.DUPLICATE_IN_FILE,
                    "message": f"Duplicate source_reference in file (first seen at row {seen_file_source_refs[src_ref]})",
                    "duplicate_reference": src_ref,
                })
            elif src_ref in db_source_refs:
                outcome = ImportRowOutcome.DUPLICATE
                duplicate_rows_count += 1
                row_errors.append({
                    "row_number": idx,
                    "column": "source_reference",
                    "code": ImportErrorCode.DUPLICATE_SOURCE_REFERENCE,
                    "message": f"Duplicate source_reference '{src_ref}' already exists in database",
                    "duplicate_reference": src_ref,
                })
            else:
                outcome = ImportRowOutcome.VALID
                valid_rows_count += 1
                seen_file_source_refs[src_ref] = idx

        row_checksum = compute_row_checksum(normalized_payload) if normalized_payload else ""
        row_model = ImportRowModel(
            id=uuid4(),
            import_job_id=job_id,
            row_number=idx,
            row_checksum=row_checksum,
            normalized_payload=normalized_payload,
            outcome=outcome.value,
            errors=row_errors if row_errors else None,
        )
        rows_to_insert.append(row_model)

    session.add_all(rows_to_insert)

    job.total_rows = total_rows_count
    job.valid_rows = valid_rows_count
    job.invalid_rows = invalid_rows_count
    job.duplicate_rows = duplicate_rows_count
    job.state = ImportJobState.VALIDATED
    await session.commit()

    return job
