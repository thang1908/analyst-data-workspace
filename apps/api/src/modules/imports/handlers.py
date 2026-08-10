import csv
import io
from uuid import UUID, uuid4
from fastapi import HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cx_contracts.common.actor import ActorContext
from cx_contracts.common.enums import ImportJobState
from cx_contracts.import_pkg.csv_v1 import TRUSTED_CSV_V1_CONTRACT_VERSION, escape_spreadsheet_formula
from cx_contracts.import_pkg.import_errors import ImportRowErrorDetail
from cx_contracts.import_pkg.import_job import (
    ExecuteJobRequest,
    ImportJobCounts,
    ImportJobCreateData,
    ImportJobCreateResponse,
    ImportJobData,
    ImportJobErrorResponse,
    ImportJobResponse,
    RetryJobRequest,
    ValidateJobRequest,
)
from cx_db.src.models.tables import ImportJobModel, ImportRowModel, ProjectModel
from apps.api.src.modules.imports.authorization import verify_import_read_permission, verify_import_write_permission
from apps.api.src.modules.imports.source_file_store import SourceFileStore
from apps.worker.src.modules.imports.execute_job import execute_import_job
from apps.worker.src.modules.imports.retry_policy import apply_job_retry
from apps.worker.src.modules.imports.validate_job import validate_import_job


file_store = SourceFileStore()


def _to_job_data(job: ImportJobModel) -> ImportJobData:
    counts = ImportJobCounts(
        total_rows=job.total_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        duplicate_rows=job.duplicate_rows,
        committed_rows=job.committed_rows,
    )
    return ImportJobData(
        job_id=job.id,
        actor_id=job.actor_id,
        project_id=job.project_id,
        idempotency_key=job.idempotency_key,
        contract_version=job.contract_version,
        file_name=job.file_name,
        file_sha256=job.file_sha256,
        state=ImportJobState(job.state),
        version=1,
        counts=counts,
        created_at=job.created_at,
        completed_at=job.completed_at,
        retryable=(job.state == ImportJobState.FAILED.value),
    )


async def handle_create_import_job(
    session: AsyncSession,
    actor: ActorContext,
    project_code: str,
    file: UploadFile,
    idempotency_key: str,
) -> ImportJobCreateResponse:
    if not (16 <= len(idempotency_key) <= 128):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key must be between 16 and 128 characters",
        )

    # 1. Lookup Project
    proj_result = await session.execute(select(ProjectModel).where(ProjectModel.code == project_code))
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project code '{project_code}' not found",
        )

    verify_import_write_permission(actor, project.id)

    # 2. Save Upload File to Store
    storage_key, file_sha256, _ = await file_store.save_upload_file(file)

    # 3. Check Idempotency Key
    existing_job_result = await session.execute(
        select(ImportJobModel).where(
            ImportJobModel.actor_id == actor.actor_id,
            ImportJobModel.idempotency_key == idempotency_key,
        )
    )
    existing_job = existing_job_result.scalar_one_or_none()
    if existing_job:
        if existing_job.file_sha256 != file_sha256:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="IDEMPOTENCY_KEY_REUSED: Same key used with different file content",
            )
        counts = ImportJobCounts(
            total_rows=existing_job.total_rows,
            valid_rows=existing_job.valid_rows,
            invalid_rows=existing_job.invalid_rows,
            duplicate_rows=existing_job.duplicate_rows,
            committed_rows=existing_job.committed_rows,
        )
        return ImportJobCreateResponse(
            data=ImportJobCreateData(
                job_id=existing_job.id,
                state=ImportJobState(existing_job.state),
                version=1,
                contract_version=existing_job.contract_version,
                file_sha256=existing_job.file_sha256,
                counts=counts,
            ),
            correlation_id=actor.correlation_id,
        )

    # 4. Create new Import Job
    new_job = ImportJobModel(
        id=uuid4(),
        actor_id=actor.actor_id,
        project_id=project.id,
        idempotency_key=idempotency_key,
        contract_version=TRUSTED_CSV_V1_CONTRACT_VERSION,
        file_name=file.filename or "upload.csv",
        file_sha256=file_sha256,
        storage_key=storage_key,
        state=ImportJobState.MAPPED.value,
    )
    session.add(new_job)
    await session.commit()

    return ImportJobCreateResponse(
        data=ImportJobCreateData(
            job_id=new_job.id,
            state=ImportJobState.MAPPED,
            version=1,
            contract_version=TRUSTED_CSV_V1_CONTRACT_VERSION,
            file_sha256=file_sha256,
            counts=ImportJobCounts(),
        ),
        correlation_id=actor.correlation_id,
    )


async def handle_get_import_job(
    session: AsyncSession,
    actor: ActorContext,
    job_id: UUID,
) -> ImportJobResponse:
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")

    verify_import_read_permission(actor, job.project_id)
    return ImportJobResponse(data=_to_job_data(job), correlation_id=actor.correlation_id)


async def handle_validate_job(
    session: AsyncSession,
    actor: ActorContext,
    job_id: UUID,
    body: ValidateJobRequest,
) -> ImportJobResponse:
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")

    verify_import_write_permission(actor, job.project_id)

    file_path = file_store.get_file_path(job.storage_key)
    with open(file_path, "rb") as f:
        file_content_bytes = f.read()

    updated_job = await validate_import_job(session, job_id, file_content_bytes)
    return ImportJobResponse(data=_to_job_data(updated_job), correlation_id=actor.correlation_id)


async def handle_execute_job(
    session: AsyncSession,
    actor: ActorContext,
    job_id: UUID,
    body: ExecuteJobRequest,
) -> ImportJobResponse:
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")

    verify_import_write_permission(actor, job.project_id)

    if job.valid_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="NO_VALID_ROWS: Job has 0 valid rows to execute",
        )

    updated_job = await execute_import_job(session, job_id, body.commit_policy)
    return ImportJobResponse(data=_to_job_data(updated_job), correlation_id=actor.correlation_id)


async def handle_retry_job(
    session: AsyncSession,
    actor: ActorContext,
    job_id: UUID,
    body: RetryJobRequest,
) -> ImportJobResponse:
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")

    verify_import_write_permission(actor, job.project_id)

    try:
        updated_job = await apply_job_retry(session, job_id, body.expected_version, body.phase)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    return ImportJobResponse(data=_to_job_data(updated_job), correlation_id=actor.correlation_id)


async def handle_get_job_errors(
    session: AsyncSession,
    actor: ActorContext,
    job_id: UUID,
    format: str = "json",
    limit: int = 50,
) -> Response:
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")

    verify_import_read_permission(actor, job.project_id)

    rows_result = await session.execute(
        select(ImportRowModel)
        .where(ImportRowModel.import_job_id == job_id, ImportRowModel.errors.is_not(None))
        .order_by(ImportRowModel.row_number.asc())
        .limit(limit)
    )
    error_rows = list(rows_result.scalars().all())

    error_items: list[ImportRowErrorDetail] = []
    for r in error_rows:
        if r.errors:
            for err in r.errors:
                error_items.append(
                    ImportRowErrorDetail(
                        row_number=err.get("row_number", r.row_number),
                        column=err.get("column"),
                        code=err["code"],
                        message=err["message"],
                        duplicate_reference=err.get("duplicate_reference"),
                    )
                )

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["row_number", "column", "error_code", "message", "duplicate_reference"])
        for item in error_items:
            writer.writerow([
                item.row_number,
                escape_spreadsheet_formula(item.column or ""),
                escape_spreadsheet_formula(item.code.value if hasattr(item.code, "value") else str(item.code)),
                escape_spreadsheet_formula(item.message),
                escape_spreadsheet_formula(item.duplicate_reference or ""),
            ])
        return Response(content=output.getvalue(), media_type="text/csv")

    response_data = ImportJobErrorResponse(
        items=error_items,
        total_count=len(error_items),
        next_cursor=None,
        correlation_id=actor.correlation_id,
    )
    return Response(content=response_data.model_dump_json(), media_type="application/json")
