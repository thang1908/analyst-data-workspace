from typing import Protocol
from uuid import UUID

from cx_domain.entities import (
    ClassificationCurrent,
    ClassificationDecision,
    Feedback,
    FeedbackItem,
    ImportJob,
    ImportRow,
    SourceRecord,
)


class ReferenceDataReader(Protocol):
    async def resolve_service_id(self, code: str) -> UUID | None: ...
    async def resolve_issue_id(self, code: str) -> UUID | None: ...
    async def resolve_location_id(self, code: str) -> UUID | None: ...


class ImportJobRepository(Protocol):
    async def get_by_id(self, job_id: UUID) -> ImportJob | None: ...
    async def get_by_idempotency_key(self, actor_id: str, idempotency_key: str) -> ImportJob | None: ...
    async def create(self, job: ImportJob) -> ImportJob: ...
    async def update_state(self, job_id: UUID, state: str, counts: dict | None = None) -> ImportJob: ...


class TrustedFeedbackUnitOfWork(Protocol):
    async def commit_row(
        self,
        import_row: ImportRow,
        source_record: SourceRecord,
        feedback: Feedback,
        item: FeedbackItem,
        decision: ClassificationDecision,
        current: ClassificationCurrent,
    ) -> None: ...


class ClassificationProjectionRepository(Protocol):
    async def rebuild(self, item_ids: list[UUID]) -> int: ...
