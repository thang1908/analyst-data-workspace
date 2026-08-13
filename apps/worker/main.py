from __future__ import annotations

import asyncio
import logging
import os
from uuid import uuid4

from apps.worker.handlers.import_handler import ImportWorkerHandler
from packages.infrastructure.db.repositories.import_job import ImportJobRepository
from packages.infrastructure.db.session import AsyncSessionLocal
from packages.infrastructure.logging import setup_logging
from packages.infrastructure.queue.postgres_queue import AsyncJobQueue
from packages.infrastructure.storage.s3 import S3StorageAdapter

setup_logging()
logger = logging.getLogger("apps.worker")


async def worker_loop() -> None:
    logger.info("Starting CX Background Worker Loop...")
    worker_id = os.getenv("WORKER_ID", f"cx-worker-{uuid4()}")
    while True:
        async with AsyncSessionLocal() as session:
            queue = AsyncJobQueue(session)
            claim = await queue.claim_next_import_job(worker_id)
            if claim is None:
                await session.commit()
                await asyncio.sleep(2)
                continue
            try:
                handler = ImportWorkerHandler(ImportJobRepository(session), S3StorageAdapter())
                if claim.resource_id is None:
                    raise ValueError("Import queue job must reference import_job_id.")
                if claim.job_type == "IMPORT_VALIDATE":
                    await handler.validate(claim.resource_id)
                elif claim.job_type == "IMPORT_EXECUTE":
                    await handler.execute(claim.resource_id)
                else:
                    raise ValueError(f"Unsupported import job type: {claim.job_type}")
                await queue.mark_completed(claim.async_job_id)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Import worker job failed", extra={"async_job_id": str(claim.async_job_id)})
                async with AsyncSessionLocal() as failure_session:
                    await AsyncJobQueue(failure_session).mark_failed(
                        claim.async_job_id, error_code="IMPORT_WORKER_FAILED", message="Import worker failed; retry is safe."
                    )
                    if claim.resource_id is not None:
                        await ImportJobRepository(failure_session).mark_failed(claim.resource_id)
                    await failure_session.commit()


def main() -> None:
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker process stopped cleanly.")


if __name__ == "__main__":
    main()
