from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from cx_contracts.common.enums import (
    DecisionSource,
    ImportJobState,
    ImportRowOutcome,
    Sentiment,
    Severity,
    ValueStatus,
)


@dataclass(frozen=True)
class Project:
    id: UUID
    code: str
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ImportJob:
    id: UUID
    actor_id: str
    project_id: UUID
    idempotency_key: str
    contract_version: str
    file_name: str
    file_sha256: str
    storage_key: str
    state: ImportJobState
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    committed_rows: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


@dataclass(frozen=True)
class ImportRow:
    id: UUID
    import_job_id: UUID
    row_number: int
    row_checksum: str
    normalized_payload: dict
    outcome: ImportRowOutcome
    errors: list[dict] | None = None


@dataclass(frozen=True)
class SourceRecord:
    id: UUID
    source: str
    source_reference: str
    import_job_id: UUID
    import_row_id: UUID
    payload_checksum: str
    created_at: datetime


@dataclass(frozen=True)
class Feedback:
    id: UUID
    source_record_id: UUID
    project_id: UUID
    reported_at: datetime
    content_masked: str
    ingested_at: datetime


@dataclass(frozen=True)
class FeedbackItem:
    id: UUID
    feedback_id: UUID
    item_index: int
    item_text_masked: str
    analytic_eligibility: str = "INCLUDED"


@dataclass(frozen=True)
class ClassificationDecision:
    id: UUID
    feedback_item_id: UUID
    decision_version: int
    primary_service_value_status: ValueStatus
    primary_service_id: UUID | None
    issue_value_status: ValueStatus
    issue_id: UUID | None
    location_value_status: ValueStatus
    location_id: UUID | None
    sentiment: Sentiment
    severity: Severity
    decision_source: DecisionSource
    decided_by: str
    decided_at: datetime
    reason: str | None = None


@dataclass(frozen=True)
class ClassificationCurrent:
    feedback_item_id: UUID
    current_decision_id: UUID
    primary_service_id: UUID | None
    issue_id: UUID | None
    location_id: UUID | None
    sentiment: Sentiment
    severity: Severity
    last_decision_at: datetime
