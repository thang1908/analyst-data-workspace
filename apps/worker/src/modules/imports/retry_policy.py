from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cx_contracts.common.enums import ImportJobState
from cx_db.src.models.tables import ImportJobModel


async def apply_job_retry(
    session: AsyncSession,
    job_id: UUID,
    expected_version: int,
    phase: str,
) -> ImportJobModel:
    """Apply retry policy to a FAILED import job."""
    result = await session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError(f"Import job not found: {job_id}")

    if job.state != ImportJobState.FAILED:
        raise ValueError(f"Cannot retry job in state '{job.state}'. Only FAILED jobs can be retried.")

    if phase == "VALIDATION":
        job.state = ImportJobState.VALIDATING
    elif phase == "EXECUTION":
        job.state = ImportJobState.QUEUED
    else:
        raise ValueError(f"Invalid retry phase '{phase}'. Expected 'VALIDATION' or 'EXECUTION'.")

    await session.commit()
    return job
