"""Import job lifecycle rules from BR-IMP-001 and BR-IMP-003."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Final, Mapping

from packages.domain.import_pipeline.entities import ImportJob
from packages.domain.import_pipeline.exceptions import InvalidImportTransitionError
from packages.domain.shared.enums import ImportJobStatus

_ALLOWED_TRANSITIONS: Final[Mapping[ImportJobStatus, frozenset[ImportJobStatus]]] = MappingProxyType(
    {
        ImportJobStatus.UPLOADED: frozenset({ImportJobStatus.MAPPED, ImportJobStatus.FAILED}),
        ImportJobStatus.MAPPED: frozenset({ImportJobStatus.VALIDATING, ImportJobStatus.FAILED}),
        ImportJobStatus.VALIDATING: frozenset({ImportJobStatus.VALIDATED, ImportJobStatus.FAILED}),
        ImportJobStatus.VALIDATED: frozenset({ImportJobStatus.QUEUED}),
        ImportJobStatus.QUEUED: frozenset({ImportJobStatus.PROCESSING, ImportJobStatus.CANCELLING}),
        ImportJobStatus.PROCESSING: frozenset({ImportJobStatus.COMPLETED, ImportJobStatus.PARTIAL, ImportJobStatus.FAILED, ImportJobStatus.CANCELLING}),
        ImportJobStatus.CANCELLING: frozenset({ImportJobStatus.CANCELLED}),
        ImportJobStatus.FAILED: frozenset({ImportJobStatus.QUEUED}),
        ImportJobStatus.PARTIAL: frozenset({ImportJobStatus.QUEUED}),
        ImportJobStatus.COMPLETED: frozenset(),
        ImportJobStatus.CANCELLED: frozenset(),
    }
)


def transition_import_job(
    job: ImportJob,
    target: ImportJobStatus,
    *,
    now: datetime | None = None,
) -> ImportJob:
    """Move a job one valid lifecycle step, retaining immutable history fields."""
    if target not in _ALLOWED_TRANSITIONS[job.status]:
        raise InvalidImportTransitionError(job.status, target)
    timestamp = now or datetime.now(timezone.utc)
    started_at = job.started_at or (timestamp if target == ImportJobStatus.PROCESSING else None)
    completed_at = timestamp if target in {
        ImportJobStatus.COMPLETED,
        ImportJobStatus.PARTIAL,
        ImportJobStatus.FAILED,
        ImportJobStatus.CANCELLED,
    } else job.completed_at
    return replace(
        job,
        status=target,
        version=job.version + 1,
        started_at=started_at,
        completed_at=completed_at,
    )
