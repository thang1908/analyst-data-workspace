"""HTTP endpoints for staged, worker-backed CSV/XLSX import."""
from __future__ import annotations

import hashlib
import os
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from apps.api.deps import get_import_job_repository, get_import_queue, get_import_storage
from apps.api.schemas.import_pipeline import (
    AsyncImportResponse,
    ExecuteImportRequest,
    ImportJobData,
    ImportJobResponse,
    MappingRequest,
)
from packages.domain.import_pipeline.entities import ImportJob
from packages.domain.import_pipeline.validation import validate_mapping
from packages.infrastructure.db.repositories.import_job import ImportJobRepository
from packages.infrastructure.queue.postgres_queue import AsyncJobQueue
from packages.infrastructure.storage.s3 import StoragePort

router = APIRouter(prefix="/api/v1/import-jobs", tags=["Import jobs"])

ImportRepositoryDep = Annotated[ImportJobRepository, Depends(get_import_job_repository)]
ImportQueueDep = Annotated[AsyncJobQueue, Depends(get_import_queue)]
ImportStorageDep = Annotated[StoragePort, Depends(get_import_storage)]
ActorId = Annotated[UUID, Header(alias="X-Actor-ID")]
CorrelationId = Annotated[str | None, Header(alias="X-Correlation-ID")]

_CONTENT_TYPES = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_CHUNK_SIZE = 1024 * 1024


@router.post("", response_model=ImportJobResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/upload", response_model=ImportJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_import_job(
    project_id: UUID,
    source_system: str,
    actor_id: ActorId,
    repository: ImportRepositoryDep,
    storage: ImportStorageDep,
    file: UploadFile = File(...),
    correlation_id: CorrelationId = None,
) -> ImportJobResponse:
    """Store an original CSV/XLSX object and create an UPLOADED import job."""
    filename = os.path.basename(file.filename or "")
    extension = os.path.splitext(filename.lower())[1]
    if extension not in _CONTENT_TYPES:
        raise HTTPException(status_code=422, detail="Only CSV and XLSX files are supported.")
    if not source_system.strip():
        raise HTTPException(status_code=422, detail="source_system must not be blank.")
    file_size, checksum = await _checksum_upload(file)
    if file_size == 0:
        raise HTTPException(status_code=422, detail="Import file must not be empty.")
    import_job_id = uuid4()
    object_key = f"imports/{project_id}/{import_job_id}/{filename}"
    content_type = _CONTENT_TYPES[extension]
    try:
        await storage.upload_fileobj(object_key, file.file, content_type=content_type)
        job = ImportJob(
            import_job_id=import_job_id,
            project_id=project_id,
            source_system=source_system.strip(),
            original_filename=filename,
            object_key=object_key,
            file_checksum=checksum,
            file_size_bytes=file_size,
            content_type=content_type,
            requested_by=actor_id,
            correlation_id=correlation_id or str(uuid4()),
        )
        await repository.create_job(job)
        return ImportJobResponse(data=_job_data(job))
    except Exception:
        await storage.delete_object(object_key)
        raise
    finally:
        await file.close()


@router.put("/{import_job_id}/mapping", response_model=ImportJobResponse)
@router.post("/{import_job_id}/map", response_model=ImportJobResponse)
async def save_import_mapping(
    import_job_id: UUID,
    request: MappingRequest,
    actor_id: ActorId,
    repository: ImportRepositoryDep,
) -> ImportJobResponse:
    """Persist a source-column mapping and move the job to MAPPED."""
    try:
        validate_mapping(request.mapping)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    job = await repository.save_mapping(
        import_job_id,
        mapping=request.mapping,
        actor_id=actor_id,
        expected_version=request.expected_version,
    )
    if job is None:
        await _raise_missing_or_conflict(repository, import_job_id)
    return ImportJobResponse(data=_job_data(job))


@router.post("/{import_job_id}/validate", response_model=AsyncImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def validate_import_job(
    import_job_id: UUID,
    repository: ImportRepositoryDep,
    queue: ImportQueueDep,
) -> AsyncImportResponse:
    """Queue streaming validation; validation never commits Feedback."""
    job = await repository.queue_validation(import_job_id)
    if job is None:
        await _raise_missing_or_conflict(repository, import_job_id)
    async_job_id = await queue.enqueue_import_job(
        job_type="IMPORT_VALIDATE", import_job_id=import_job_id, correlation_id=job.correlation_id
    )
    return AsyncImportResponse(data=_job_data(job), async_job_id=async_job_id)


@router.post("/{import_job_id}/execute", response_model=AsyncImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_import_job(
    import_job_id: UUID,
    request: ExecuteImportRequest,
    repository: ImportRepositoryDep,
    queue: ImportQueueDep,
) -> AsyncImportResponse:
    """Queue idempotent execution from a VALIDATED import job."""
    current_job = await repository.get_job(import_job_id)
    if current_job is None:
        raise HTTPException(status_code=404, detail="Import job was not found.")
    if not request.allow_partial and (current_job.invalid_rows or 0) > 0:
        raise HTTPException(status_code=422, detail="Import has invalid rows; allow_partial is required.")
    job = await repository.queue_execution(import_job_id, expected_version=request.expected_version)
    if job is None:
        await _raise_missing_or_conflict(repository, import_job_id)
    async_job_id = await queue.enqueue_import_job(
        job_type="IMPORT_EXECUTE", import_job_id=import_job_id, correlation_id=job.correlation_id
    )
    return AsyncImportResponse(data=_job_data(job), async_job_id=async_job_id)


@router.get("/{import_job_id}", response_model=ImportJobResponse)
async def get_import_job(import_job_id: UUID, repository: ImportRepositoryDep) -> ImportJobResponse:
    job = await repository.get_job(import_job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Import job was not found.")
    return ImportJobResponse(data=_job_data(job))


async def _checksum_upload(file: UploadFile) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    while chunk := await file.read(_CHUNK_SIZE):
        digest.update(chunk)
        size += len(chunk)
    await file.seek(0)
    return size, digest.hexdigest()


def _job_data(job: ImportJob) -> ImportJobData:
    return ImportJobData(
        import_job_id=job.import_job_id,
        status=job.status.value,
        filename=job.original_filename,
        file_size_bytes=job.file_size_bytes,
        total_rows=job.total_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        committed_rows=job.committed_rows,
        error_object_key=job.error_object_key,
        created_at=job.created_at,
        version=job.version,
    )


async def _raise_missing_or_conflict(
    repository: ImportJobRepository, import_job_id: UUID
) -> None:
    if await repository.get_job(import_job_id) is None:
        raise HTTPException(status_code=404, detail="Import job was not found.")
    raise HTTPException(status_code=409, detail="Import job state or version no longer permits this action.")
