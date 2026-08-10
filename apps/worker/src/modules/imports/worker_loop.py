import asyncio
import logging
from sqlalchemy import select
from cx_contracts.common.enums import ImportJobState
from cx_db.src.models.tables import ImportJobModel
from cx_db.src.session import AsyncSessionLocal
from apps.worker.src.modules.imports.validate_job import validate_import_job
from apps.worker.src.modules/imports.execute_job import execute_import_job
from apps.api.src.modules.imports.source_file_store import SourceFileStore

logger = logging.getLogger("cx-worker-import")


async def process_queued_import_jobs() -> None:
    """Poll for QUEUED or MAPPED import jobs and process them."""
    file_store = SourceFileStore()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ImportJobModel).where(
                ImportJobModel.state.in_([ImportJobState.MAPPED.value, ImportJobState.QUEUED.value])
            )
        )
        jobs = list(result.scalars().all())
        for job in jobs:
            try:
                if job.state == ImportJobState.MAPPED.value:
                    logger.info(f"Worker validating job {job.id}...")
                    file_path = file_store.get_file_path(job.storage_key)
                    with open(file_path, "rb") as f:
                        content_bytes = f.read()
                    await validate_import_job(session, job.id, content_bytes)

                elif job.state == ImportJobState.QUEUED.value:
                    logger.info(f"Worker executing job {job.id}...")
                    await execute_import_job(session, job.id)

            except Exception as e:
                logger.error(f"Error processing import job {job.id}: {e}", exc_info=True)
                job.state = ImportJobState.FAILED
                await session.commit()
