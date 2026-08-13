"""Unit tests for task #11 import-pipeline domain and application rules."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from packages.application.import_pipeline.import_service import ImportValidationService
from packages.domain.import_pipeline.entities import ImportJob
from packages.domain.import_pipeline.exceptions import InvalidImportTransitionError
from packages.domain.import_pipeline.state_machine import transition_import_job
from packages.domain.import_pipeline.validation import idempotency_key, validate_mapping, validate_rows
from packages.domain.shared.enums import ImportJobStatus


def _job(status: ImportJobStatus = ImportJobStatus.UPLOADED) -> ImportJob:
    return ImportJob(
        project_id=uuid4(), source_system="resident-app", original_filename="feedback.csv",
        object_key="imports/feedback.csv", file_checksum="sha256", file_size_bytes=12,
        content_type="text/csv", requested_by=uuid4(), correlation_id="test", status=status,
    )


def _mapped_job() -> ImportJob:
    return transition_import_job(_job(), ImportJobStatus.MAPPED)


def test_state_machine_enforces_the_documented_async_lifecycle() -> None:
    job = _job()
    for target in (
        ImportJobStatus.MAPPED, ImportJobStatus.VALIDATING, ImportJobStatus.VALIDATED,
        ImportJobStatus.QUEUED, ImportJobStatus.PROCESSING, ImportJobStatus.COMPLETED,
    ):
        job = transition_import_job(job, target)
    assert job.status == ImportJobStatus.COMPLETED
    assert job.version == 7
    assert job.started_at is not None
    assert job.completed_at is not None


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ImportJobStatus.UPLOADED, ImportJobStatus.QUEUED),
        (ImportJobStatus.MAPPED, ImportJobStatus.PROCESSING),
        (ImportJobStatus.VALIDATED, ImportJobStatus.PROCESSING),
        (ImportJobStatus.COMPLETED, ImportJobStatus.QUEUED),
    ],
)
def test_state_machine_rejects_lifecycle_shortcuts(
    current: ImportJobStatus, target: ImportJobStatus
) -> None:
    with pytest.raises(InvalidImportTransitionError):
        transition_import_job(_job(current), target)


def test_row_validation_retains_missing_invalid_and_duplicate_outcomes() -> None:
    rows = validate_rows(
        source_system="resident-app",
        mapping={"source_record_key": "id", "reported_at": "reported", "content": "message"},
        raw_rows=[
            {"id": "first", "reported": "2026-08-10T09:00:00Z", "message": "Valid feedback"},
            {"id": "first", "reported": "2026-08-10T09:00:00Z", "message": "Duplicate feedback"},
            {"id": "existing", "reported": "not-a-date", "message": "Already imported"},
            {"id": "missing-content", "reported": "", "message": " "},
        ],
        existing_source_record_keys=frozenset({"existing"}),
    )

    assert [row.validation_status for row in rows] == ["VALID", "INVALID", "INVALID", "INVALID"]
    assert rows[1].errors[0].error_code == "DUPLICATE_IN_FILE"
    assert {error.error_code for error in rows[2].errors} == {"DUPLICATE_SOURCE_RECORD", "INVALID_DATETIME"}
    assert rows[3].event_time_inferred is True
    assert rows[3].errors[0].error_code == "REQUIRED_FIELD"


def test_missing_source_key_uses_deterministic_fallback_identity() -> None:
    normalized = {"content": "Same text", "reported_at": "2026-08-10T09:00:00Z"}
    assert idempotency_key("resident-app", normalized) == idempotency_key("resident-app", normalized)


def test_schema_error_fails_job_without_creating_row_outcomes() -> None:
    result = ImportValidationService().validate(
        job=_mapped_job(), mapping={"reported_at": "date"}, raw_rows=[{"date": "2026-08-10"}],
    )

    assert result.job.status == ImportJobStatus.FAILED
    assert result.rows == ()
    assert result.file_errors[0].error_code == "VALIDATION_ERROR"


def test_validation_never_commits_feedback_and_allows_partial_execution() -> None:
    result = ImportValidationService().validate(
        job=_mapped_job(),
        mapping={"source_record_key": "id", "content": "message"},
        raw_rows=[{"id": "1", "message": "Valid"}, {"id": "2", "message": ""}],
    )

    assert result.job.status == ImportJobStatus.VALIDATED
    assert (result.job.total_rows, result.job.valid_rows, result.job.invalid_rows, result.job.committed_rows) == (2, 1, 1, 0)
    assert all(row.commit_status == "PENDING" for row in result.rows)
    assert ImportValidationService().queue_execution(result.job).status == ImportJobStatus.QUEUED


def test_mapping_rejects_ambiguous_or_missing_required_columns() -> None:
    with pytest.raises(Exception, match="required"):
        validate_mapping({"reported_at": "date"})
    with pytest.raises(Exception, match="one canonical"):
        validate_mapping({"content": "text", "source_record_key": "text"})
