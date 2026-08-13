"""Application use cases that orchestrate pure import domain rules."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping

from packages.domain.import_pipeline.entities import ImportJob, ImportRow, ImportRowError
from packages.domain.import_pipeline.exceptions import ImportSchemaError
from packages.domain.import_pipeline.state_machine import transition_import_job
from packages.domain.import_pipeline.validation import validate_rows
from packages.domain.shared.enums import ImportJobStatus


@dataclass(frozen=True, slots=True)
class ImportValidationResult:
    """The persisted-row-ready result of preview/validation, without Feedback writes."""

    job: ImportJob
    rows: tuple[ImportRow, ...]
    file_errors: tuple[ImportRowError, ...] = ()

    @property
    def valid_rows(self) -> int:
        return sum(row.is_valid for row in self.rows)

    @property
    def invalid_rows(self) -> int:
        return len(self.rows) - self.valid_rows


class ImportValidationService:
    """Run non-committing row validation and the VALIDATING → VALIDATED transition."""

    def validate(
        self,
        *,
        job: ImportJob,
        mapping: Mapping[str, str],
        raw_rows: Iterable[Mapping[str, Any]],
        existing_source_record_keys: frozenset[str] = frozenset(),
    ) -> ImportValidationResult:
        validating_job = transition_import_job(job, ImportJobStatus.VALIDATING)
        try:
            rows = tuple(
                validate_rows(
                    source_system=job.source_system,
                    mapping=mapping,
                    raw_rows=raw_rows,
                    existing_source_record_keys=existing_source_record_keys,
                )
            )
        except ImportSchemaError as error:
            return ImportValidationResult(
                job=transition_import_job(validating_job, ImportJobStatus.FAILED),
                rows=(),
                file_errors=(ImportRowError(error.code, error.message, severity="ERROR", metadata=error.details),),
            )
        validated_job = transition_import_job(validating_job, ImportJobStatus.VALIDATED)
        final_job = replace(
            validated_job,
            total_rows=len(rows),
            valid_rows=sum(row.is_valid for row in rows),
            invalid_rows=sum(not row.is_valid for row in rows),
            committed_rows=0,
        )
        return ImportValidationResult(job=final_job, rows=rows)

    def queue_execution(self, job: ImportJob) -> ImportJob:
        """Enforce BR-IMP-003: only a validated job can enter the worker queue."""
        return transition_import_job(job, ImportJobStatus.QUEUED)
