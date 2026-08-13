"""PostgreSQL integration test for the import worker's validation and batched commit path."""
from __future__ import annotations

import io
import os
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.worker.handlers.import_handler import ImportWorkerHandler
from packages.infrastructure.db.repositories.import_job import ImportJobRepository
from packages.infrastructure.db.session import engine
from packages.infrastructure.storage.s3 import StoragePort

if os.getenv("RUN_IMPORT_INTEGRATION_TESTS") != "1":
    pytestmark = pytest.mark.skip(
        reason="set RUN_IMPORT_INTEGRATION_TESTS=1 to use local PostgreSQL"
    )


class MemoryStorage(StoragePort):
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = objects

    async def generate_presigned_url(self, object_name: str, client_action: str = "get_object", expires_in: int = 3600) -> str:
        return f"memory://{object_name}"

    async def delete_object(self, object_name: str) -> bool:
        self.objects.pop(object_name, None)
        return True

    async def download_fileobj(self, object_name: str, destination: io.BytesIO) -> None:
        destination.write(self.objects[object_name])
        destination.seek(0)

    async def upload_fileobj(self, object_name: str, source: io.BytesIO, *, content_type: str) -> None:
        self.objects[object_name] = source.read()


@pytest.mark.asyncio
async def test_import_worker_validates_and_commits_with_lineage_in_real_postgres() -> None:
    project_id, actor_id, mapping_id, import_job_id = uuid4(), uuid4(), uuid4(), uuid4()
    object_key = f"integration/{import_job_id}.csv"
    storage = MemoryStorage({
        object_key: (
            b"ticket_id,message,reported_date\n"
            b"valid-1,Toi can ho tro,2026-08-13T08:00:00Z\n"
            b"invalid-1,,2026-08-13T08:00:00Z\n"
        )
    })
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            await session.execute(
                text("""
                    INSERT INTO import_mapping_profile (
                        import_mapping_profile_id, project_id, name, source_system,
                        mapping_json, created_by
                    ) VALUES (
                        :mapping_id, :project_id, 'integration mapping', 'import-integration',
                        CAST(:mapping_json AS jsonb), :actor_id
                    )
                """),
                {
                    "mapping_id": mapping_id,
                    "project_id": project_id,
                    "actor_id": actor_id,
                    "mapping_json": '{"ticket_id":"source_record_key","message":"content","reported_date":"reported_at"}',
                },
            )
            await session.execute(
                text("""
                    INSERT INTO import_job (
                        import_job_id, project_id, source_system, original_filename, object_key,
                        file_checksum, file_size_bytes, content_type, status, mapping_profile_id,
                        requested_by, correlation_id
                    ) VALUES (
                        :import_job_id, :project_id, 'import-integration', 'feedback.csv', :object_key,
                        'checksum', 100, 'text/csv', 'VALIDATING', :mapping_id, :actor_id, 'integration'
                    )
                """),
                {
                    "import_job_id": import_job_id,
                    "project_id": project_id,
                    "object_key": object_key,
                    "mapping_id": mapping_id,
                    "actor_id": actor_id,
                },
            )
            repository = ImportJobRepository(session)
            handler = ImportWorkerHandler(repository, storage)

            assert await handler.validate(import_job_id) == "VALIDATED"
            validation = (await session.execute(
                text("SELECT status, total_rows, valid_rows, invalid_rows, error_object_key FROM import_job WHERE import_job_id = :id"),
                {"id": import_job_id},
            )).mappings().one()
            assert dict(validation) == {
                "status": "VALIDATED", "total_rows": 2, "valid_rows": 1, "invalid_rows": 1,
                "error_object_key": f"imports/{import_job_id}/error_report.csv",
            }
            assert b"REQUIRED_FIELD" in storage.objects[f"imports/{import_job_id}/error_report.csv"]

            await session.execute(
                text("UPDATE import_job SET status = 'QUEUED' WHERE import_job_id = :id"),
                {"id": import_job_id},
            )
            assert await handler.execute(import_job_id) == "PARTIAL"
            committed = (await session.execute(
                text("""
                    SELECT job.committed_rows, row.commit_status, feedback.import_job_id
                    FROM import_job AS job
                    INNER JOIN import_row AS row ON row.import_job_id = job.import_job_id
                    LEFT JOIN feedback ON feedback.feedback_id = row.feedback_id
                    WHERE job.import_job_id = :id AND row.source_record_key = 'valid-1'
                """),
                {"id": import_job_id},
            )).mappings().one()
            assert dict(committed) == {
                "committed_rows": 1,
                "commit_status": "COMMITTED",
                "import_job_id": import_job_id,
            }
        finally:
            await session.close()
            await transaction.rollback()
