"""Immutable import lifecycle and row-lineage entities."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4

from packages.domain.shared.enums import ImportJobStatus


@dataclass(frozen=True, slots=True)
class ImportJob:
    """One asynchronous import request, without persistence dependencies."""

    project_id: UUID
    source_system: str
    original_filename: str
    object_key: str
    file_checksum: str
    file_size_bytes: int
    content_type: str
    requested_by: UUID
    correlation_id: str
    import_job_id: UUID = field(default_factory=uuid4)
    status: ImportJobStatus = ImportJobStatus.UPLOADED
    version: int = 1
    total_rows: int | None = None
    valid_rows: int | None = None
    invalid_rows: int | None = None
    committed_rows: int | None = None
    error_object_key: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def with_status(self, status: ImportJobStatus, *, now: datetime | None = None) -> ImportJob:
        """Return a version-bumped job after a validated state transition."""
        from packages.domain.import_pipeline.state_machine import transition_import_job

        return transition_import_job(self, status, now=now)


@dataclass(frozen=True, slots=True)
class ImportRowError:
    """A non-silent validation outcome retained for one source row."""

    error_code: str
    message: str
    field_name: str | None = None
    severity: str = "ERROR"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ImportRow:
    """Normalized source row with idempotency identity and validation outcome."""

    row_number: int
    idempotency_key: str
    raw_row: Mapping[str, Any]
    normalized_row: Mapping[str, Any]
    source_record_key: str | None
    validation_status: str
    commit_status: str = "PENDING"
    errors: tuple[ImportRowError, ...] = ()
    event_time_inferred: bool = False

    @property
    def is_valid(self) -> bool:
        return self.validation_status == "VALID"

    @property
    def is_committed(self) -> bool:
        return self.commit_status == "COMMITTED"
