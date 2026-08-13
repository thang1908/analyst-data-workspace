"""HTTP contracts for the staged import API without requiring S3 or PostgreSQL."""
from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from apps.api.deps import get_import_job_repository, get_import_queue, get_import_storage
from apps.api.main import app
from packages.domain.import_pipeline.entities import ImportJob
from packages.domain.shared.enums import ImportJobStatus


class StubImportRepository:
    def __init__(self) -> None:
        self.jobs: dict[UUID, ImportJob] = {}

    async def create_job(self, job: ImportJob) -> ImportJob:
        self.jobs[job.import_job_id] = job
        return job

    async def get_job(self, import_job_id: UUID) -> ImportJob | None:
        return self.jobs.get(import_job_id)

    async def save_mapping(self, import_job_id: UUID, *, mapping: dict[str, str], actor_id: UUID, expected_version: int) -> ImportJob | None:
        del mapping, actor_id
        job = self.jobs.get(import_job_id)
        if job is None or job.version != expected_version:
            return None
        mapped = replace(job, status=ImportJobStatus.MAPPED, version=job.version + 1)
        self.jobs[import_job_id] = mapped
        return mapped

    async def queue_validation(self, import_job_id: UUID) -> ImportJob | None:
        job = self.jobs.get(import_job_id)
        if job is None or job.status is not ImportJobStatus.MAPPED:
            return None
        queued = replace(job, status=ImportJobStatus.VALIDATING, version=job.version + 1)
        self.jobs[import_job_id] = queued
        return queued

    async def queue_execution(self, import_job_id: UUID, *, expected_version: int) -> ImportJob | None:
        job = self.jobs.get(import_job_id)
        if job is None or job.status is not ImportJobStatus.VALIDATED or job.version != expected_version:
            return None
        queued = replace(job, status=ImportJobStatus.QUEUED, version=job.version + 1)
        self.jobs[import_job_id] = queued
        return queued


class StubQueue:
    def __init__(self) -> None:
        self.enqueued: list[tuple[str, UUID]] = []

    async def enqueue_import_job(self, *, job_type: str, import_job_id: UUID, correlation_id: str) -> UUID:
        del correlation_id
        self.enqueued.append((job_type, import_job_id))
        return uuid4()


class StubStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def upload_fileobj(self, object_name: str, source: object, *, content_type: str) -> None:
        del content_type
        self.objects[object_name] = source.read()  # type: ignore[attr-defined]

    async def delete_object(self, object_name: str) -> bool:
        self.objects.pop(object_name, None)
        return True


def _client() -> tuple[TestClient, StubImportRepository, StubQueue, StubStorage]:
    repository, queue, storage = StubImportRepository(), StubQueue(), StubStorage()
    app.dependency_overrides[get_import_job_repository] = lambda: repository
    app.dependency_overrides[get_import_queue] = lambda: queue
    app.dependency_overrides[get_import_storage] = lambda: storage
    return TestClient(app), repository, queue, storage


def test_upload_recognises_csv_and_rejects_unsupported_format() -> None:
    client, _, _, storage = _client()
    try:
        response = client.post(
            "/api/v1/import-jobs/upload",
            params={"project_id": uuid4(), "source_system": "resident-app"},
            headers={"X-Actor-ID": str(uuid4())},
            files={"file": ("feedback.csv", b"ticket_id,message\n1,Hello\n", "text/csv")},
        )
        invalid = client.post(
            "/api/v1/import-jobs/upload",
            params={"project_id": uuid4(), "source_system": "resident-app"},
            headers={"X-Actor-ID": str(uuid4())},
            files={"file": ("feedback.pdf", b"not supported", "application/pdf")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["data"]["status"] == "UPLOADED"
    assert response.json()["data"]["filename"] == "feedback.csv"
    assert len(storage.objects) == 1
    assert invalid.status_code == 422


def test_mapping_validation_and_execute_enqueue_contract() -> None:
    client, repository, queue, _ = _client()
    import_job_id = uuid4()
    actor_id = uuid4()
    repository.jobs[import_job_id] = ImportJob(
        import_job_id=import_job_id,
        project_id=uuid4(), source_system="resident-app", original_filename="feedback.csv",
        object_key="imports/feedback.csv", file_checksum="checksum", file_size_bytes=2,
        content_type="text/csv", requested_by=actor_id, correlation_id="test",
    )
    try:
        mapped = client.post(
            f"/api/v1/import-jobs/{import_job_id}/map",
            headers={"X-Actor-ID": str(actor_id)},
            json={"expected_version": 1, "mapping": {"ticket_id": "source_record_key", "message": "content"}},
        )
        validation = client.post(f"/api/v1/import-jobs/{import_job_id}/validate")
        repository.jobs[import_job_id] = replace(
            repository.jobs[import_job_id],
            status=ImportJobStatus.VALIDATED,
            version=4,
            invalid_rows=1,
        )
        blocked = client.post(
            f"/api/v1/import-jobs/{import_job_id}/execute",
            json={"expected_version": 4, "allow_partial": False},
        )
        executed = client.post(
            f"/api/v1/import-jobs/{import_job_id}/execute",
            json={"expected_version": 4, "allow_partial": True},
        )
    finally:
        app.dependency_overrides.clear()

    assert mapped.status_code == 200
    assert validation.status_code == 202
    assert blocked.status_code == 422
    assert executed.status_code == 202
    assert queue.enqueued == [("IMPORT_VALIDATE", import_job_id), ("IMPORT_EXECUTE", import_job_id)]
