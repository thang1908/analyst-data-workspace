"""FastAPI application dependencies."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.infrastructure.db.repositories.import_job import ImportJobRepository
from packages.infrastructure.db.session import get_db_session
from packages.infrastructure.queue.postgres_queue import AsyncJobQueue
from packages.infrastructure.storage.s3 import S3StorageAdapter, StoragePort


async def get_import_job_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[ImportJobRepository, None]:
    yield ImportJobRepository(session)


async def get_import_queue(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AsyncJobQueue, None]:
    yield AsyncJobQueue(session)


async def get_import_storage() -> AsyncGenerator[StoragePort, None]:
    yield S3StorageAdapter()
