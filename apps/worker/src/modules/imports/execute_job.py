from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cx_contracts.common.enums import (
    DecisionSource,
    ImportJobState,
    ImportRowOutcome,
    Sentiment,
    Severity,
    ValueStatus,
)
from cx_contracts.import_pkg.csv_v1 import compute_row_checksum
from cx_contracts.import_pkg.import_errors import ImportErrorCode
from cx_db.src.models.tables import (
    ClassificationCurrentModel,
    ClassificationDecisionModel,
    FeedbackItemModel,
    FeedbackModel,
    ImportJobModel,
    ImportRowModel,
    LocationNodeModel,
    OutboxEventModel,
    SourceRecordModel,
    TaxonomyIssueModel,
    TaxonomyServiceModel,
)

CHUNK_SIZE = 200


async def execute_import_job(
    session: AsyncSession,
    job_id: UUID,
    commit_policy: str = "VALID_ROWS_ONLY",
) -> ImportJobModel:
    """Execute import job committing valid rows atomically in chunks."""
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError(f"Import job not found: {job_id}")

    if job.valid_rows == 0:
        raise ValueError("No valid rows to execute")

    job.state = ImportJobState.PROCESSING
    await session.commit()

    # Pre-load maps for resolving entity IDs
    locations_result = await session.execute(
        select(LocationNodeModel.code, LocationNodeModel.id).where(
            LocationNodeModel.project_id == job.project_id
        )
    )
    location_map = {row[0]: row[1] for row in locations_result.all()}

    services_result = await session.execute(select(TaxonomyServiceModel.code, TaxonomyServiceModel.id))
    service_map = {row[0]: row[1] for row in services_result.all()}

    issues_result = await session.execute(select(TaxonomyIssueModel.code, TaxonomyIssueModel.id))
    issue_map = {row[0]: row[1] for row in issues_result.all()}

    # Fetch valid rows
    valid_rows_result = await session.execute(
        select(ImportRowModel)
        .where(
            ImportRowModel.import_job_id == job_id,
            ImportRowModel.outcome == ImportRowOutcome.VALID.value,
        )
        .order_by(ImportRowModel.row_number.asc())
    )
    valid_rows = list(valid_rows_result.scalars().all())

    # Process in chunks
    for i in range(0, len(valid_rows), CHUNK_SIZE):
        chunk = valid_rows[i : i + CHUNK_SIZE]
        for row in chunk:
            payload = row.normalized_payload
            src_ref = payload.get("source_reference", "")

            # Idempotency / concurrent duplicate check
            existing_ref_result = await session.execute(
                select(SourceRecordModel.id).where(
                    SourceRecordModel.source == "PILOT_CSV_V1",
                    SourceRecordModel.source_reference == src_ref,
                )
            )
            if existing_ref_result.scalar_one_or_none() is not None:
                # Marked as concurrent duplicate
                row.outcome = ImportRowOutcome.DUPLICATE.value
                row.errors = [{
                    "row_number": row.row_number,
                    "column": "source_reference",
                    "code": ImportErrorCode.DUPLICATE_SOURCE_REFERENCE.value,
                    "message": f"Concurrent duplicate source_reference '{src_ref}'",
                    "duplicate_reference": src_ref,
                }]
                job.valid_rows -= 1
                job.duplicate_rows += 1
                continue

            # Create canonical chain
            now = datetime.now(timezone.utc)
            source_rec_id = uuid4()
            feedback_id = uuid4()
            feedback_item_id = uuid4()
            decision_id = uuid4()

            rep_at = datetime.fromisoformat(payload["reported_at"])
            cnt_masked = payload["content_masked"]
            loc_id = location_map.get(payload.get("location_code", ""))
            srv_id = service_map.get(payload.get("service_code", ""))
            iss_id = issue_map.get(payload.get("issue_code", ""))
            sent_str = payload.get("sentiment", "NEUTRAL")
            sev_str = payload.get("operational_severity", "SEV-3")

            # 1. SourceRecord
            source_rec = SourceRecordModel(
                id=source_rec_id,
                source="PILOT_CSV_V1",
                source_reference=src_ref,
                import_job_id=job_id,
                import_row_id=row.id,
                payload_checksum=row.row_checksum or compute_row_checksum(payload),
            )
            session.add(source_rec)

            # 2. Feedback
            feedback = FeedbackModel(
                id=feedback_id,
                source_record_id=source_rec_id,
                project_id=job.project_id,
                reported_at=rep_at,
                content_masked=cnt_masked,
            )
            session.add(feedback)

            # 3. FeedbackItem
            feedback_item = FeedbackItemModel(
                id=feedback_item_id,
                feedback_id=feedback_id,
                item_index=1,
                item_text_masked=cnt_masked,
                analytic_eligibility="INCLUDED",
            )
            session.add(feedback_item)

            # 4. ClassificationDecision
            decision = ClassificationDecisionModel(
                id=decision_id,
                feedback_item_id=feedback_item_id,
                decision_version=1,
                primary_service_value_status=ValueStatus.KNOWN.value if srv_id else ValueStatus.MISSING.value,
                primary_service_id=srv_id,
                issue_value_status=ValueStatus.KNOWN.value if iss_id else ValueStatus.MISSING.value,
                issue_id=iss_id,
                location_value_status=ValueStatus.KNOWN.value if loc_id else ValueStatus.MISSING.value,
                location_id=loc_id,
                sentiment=sent_str,
                severity=sev_str,
                decision_source=DecisionSource.SOURCE_TRUSTED.value,
                decided_by=job.actor_id,
                reason="Imported via trusted CSV v1",
            )
            session.add(decision)

            # 5. ClassificationCurrent
            current = ClassificationCurrentModel(
                feedback_item_id=feedback_item_id,
                current_decision_id=decision_id,
                primary_service_id=srv_id,
                issue_id=iss_id,
                location_id=loc_id,
                sentiment=sent_str,
                severity=sev_str,
                last_decision_at=now,
            )
            session.add(current)

            # 6. OutboxEvent
            outbox = OutboxEventModel(
                id=uuid4(),
                dedupe_key=f"import_committed_{row.id}",
                event_type="FEEDBACK_INGESTED",
                schema_version="v1",
                aggregate_id=feedback_id,
                payload={"job_id": str(job_id), "source_reference": src_ref},
            )
            session.add(outbox)

            job.committed_rows += 1

        await session.commit()

    # Finalize state
    if job.invalid_rows > 0:
        job.state = ImportJobState.PARTIAL
    else:
        job.state = ImportJobState.COMPLETED

    job.completed_at = datetime.now(timezone.utc)
    await session.commit()

    return job
