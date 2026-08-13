"""Persistence gateway for retry-safe import validation and execution."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.import_pipeline.import_service import ImportValidationResult
from packages.domain.import_pipeline.entities import ImportJob, ImportRow, ImportRowError
from packages.domain.shared.enums import ImportJobStatus

_ROW_INSERT_SQL = text("""
    INSERT INTO import_row (
        import_job_id, row_number, source_record_key, idempotency_key,
        raw_row_json, normalized_row_json, validation_status, commit_status
    ) VALUES (
        :import_job_id, :row_number, :source_record_key, :idempotency_key,
        CAST(:raw_row_json AS jsonb), CAST(:normalized_row_json AS jsonb),
        :validation_status, :commit_status
    )
""")

_ERROR_INSERT_SQL = text("""
    INSERT INTO import_row_error (
        import_row_id, field_name, error_code, message, severity, metadata_json
    ) VALUES (
        :import_row_id, :field_name, :error_code, :message, :severity,
        CAST(:metadata_json AS jsonb)
    )
""")


@dataclass(frozen=True, slots=True)
class ImportExecutionContext:
    """The immutable data a worker needs without exposing raw content in logs."""

    job: ImportJob
    mapping: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class PersistedImportRow:
    import_row_id: UUID
    source_record_key: str | None
    idempotency_key: str
    normalized_row: Mapping[str, Any]


class ImportJobRepository:
    """SQL repository for import-job lifecycle, lineage and batched feedback writes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_context(self, import_job_id: UUID) -> ImportExecutionContext:
        result = await self._session.execute(
            text("""
                SELECT job.*, profile.mapping_json
                FROM import_job AS job
                LEFT JOIN import_mapping_profile AS profile
                  ON profile.import_mapping_profile_id = job.mapping_profile_id
                WHERE job.import_job_id = :import_job_id
            """),
            {"import_job_id": import_job_id},
        )
        row = result.mappings().one()
        mapping = dict(row["mapping_json"] or {})
        if not mapping:
            raise ValueError("Import job has no persisted mapping profile.")
        return ImportExecutionContext(job=_as_domain_job(row), mapping=mapping)

    async def source_record_keys(self, source_system: str) -> frozenset[str]:
        result = await self._session.execute(
            text("""
                SELECT source_record_key
                FROM feedback
                WHERE source_system = :source_system AND source_record_key IS NOT NULL
            """),
            {"source_system": source_system},
        )
        return frozenset(str(value) for value in result.scalars().all())

    async def persist_validation(
        self,
        import_job_id: UUID,
        validation: ImportValidationResult,
        *,
        error_object_key: str | None,
    ) -> None:
        """Replace validation lineage atomically; feedback is never inserted here."""
        await self._session.execute(
            text("DELETE FROM import_row WHERE import_job_id = :import_job_id"),
            {"import_job_id": import_job_id},
        )
        rows = list(validation.rows)
        for batch in _batches(rows, 500):
            await self._session.execute(
                _ROW_INSERT_SQL,
                [_row_parameters(import_job_id, row) for row in batch],
            )
        if rows:
            ids = await self._session.execute(
                text("""
                    SELECT import_row_id, row_number
                    FROM import_row
                    WHERE import_job_id = :import_job_id
                """),
                {"import_job_id": import_job_id},
            )
            row_ids = {int(row.row_number): row.import_row_id for row in ids}
            error_values = [
                _error_parameters(row_ids[row.row_number], error)
                for row in rows
                for error in row.errors
            ]
            for batch in _batches(error_values, 500):
                await self._session.execute(_ERROR_INSERT_SQL, batch)
        await self._session.execute(
            text("""
                UPDATE import_job
                SET status = :status, total_rows = :total_rows, valid_rows = :valid_rows,
                    invalid_rows = :invalid_rows, committed_rows = 0,
                    error_object_key = :error_object_key,
                    completed_at = CASE WHEN :status = 'FAILED' THEN now() ELSE NULL END,
                    version = version + 1
                WHERE import_job_id = :import_job_id
            """),
            {
                "import_job_id": import_job_id,
                "status": validation.job.status.value,
                "total_rows": validation.job.total_rows,
                "valid_rows": validation.job.valid_rows,
                "invalid_rows": validation.job.invalid_rows,
                "error_object_key": error_object_key,
            },
        )

    async def start_execution(self, import_job_id: UUID) -> bool:
        result = await self._session.execute(
            text("""
                UPDATE import_job
                SET status = 'PROCESSING', started_at = COALESCE(started_at, now()), version = version + 1
                WHERE import_job_id = :import_job_id AND status = 'QUEUED'
            """),
            {"import_job_id": import_job_id},
        )
        return bool(result.rowcount)

    async def valid_uncommitted_rows(self, import_job_id: UUID) -> list[PersistedImportRow]:
        result = await self._session.execute(
            text("""
                SELECT import_row_id, source_record_key, idempotency_key, normalized_row_json
                FROM import_row
                WHERE import_job_id = :import_job_id
                  AND validation_status = 'VALID'
                  AND commit_status = 'PENDING'
                ORDER BY row_number
            """),
            {"import_job_id": import_job_id},
        )
        return [
            PersistedImportRow(
                import_row_id=row.import_row_id,
                source_record_key=row.source_record_key,
                idempotency_key=row.idempotency_key,
                normalized_row=dict(row.normalized_row_json or {}),
            )
            for row in result.mappings().all()
        ]

    async def commit_rows(
        self, context: ImportExecutionContext, rows: Iterable[PersistedImportRow]
    ) -> int:
        """Upsert Feedback + first FeedbackItem and update lineage in one DB batch."""
        payload = _commit_payload(context.job, rows)
        if not payload:
            return 0
        params = {
            "project_id": context.job.project_id,
            "source_system": context.job.source_system,
            "import_job_id": context.job.import_job_id,
            "rows_json": json.dumps(payload),
        }
        await self._session.execute(
            text("""
                WITH rows AS (
                    SELECT * FROM jsonb_to_recordset(CAST(:rows_json AS jsonb)) AS value(
                        import_row_id uuid, source_record_key text, reported_at timestamptz,
                        content_raw text, content_masked text, checksum text
                    )
                )
                INSERT INTO feedback (
                    project_id, source_system, source_record_key, reported_at,
                    content_raw, content_masked, source_metadata_json, import_job_id,
                    import_row_id, raw_content_checksum
                )
                SELECT :project_id, :source_system, source_record_key, reported_at,
                       content_raw, content_masked, '{}'::jsonb, :import_job_id,
                       import_row_id, checksum
                FROM rows
                ON CONFLICT (source_system, source_record_key) DO NOTHING
            """),
            params,
        )
        await self._session.execute(
            text("""
                WITH rows AS (
                    SELECT * FROM jsonb_to_recordset(CAST(:rows_json AS jsonb)) AS value(
                        import_row_id uuid, source_record_key text, reported_at timestamptz,
                        content_raw text, content_masked text, checksum text
                    )
                )
                INSERT INTO feedback_item (feedback_id, item_index, item_text_masked, analytic_eligibility)
                SELECT feedback.feedback_id, 1, rows.content_masked, 'PENDING'
                FROM rows
                INNER JOIN feedback
                  ON feedback.source_system = :source_system
                 AND feedback.source_record_key = rows.source_record_key
                ON CONFLICT (feedback_id, item_index) DO NOTHING
            """),
            params,
        )
        result = await self._session.execute(
            text("""
                WITH rows AS (
                    SELECT * FROM jsonb_to_recordset(CAST(:rows_json AS jsonb)) AS value(
                        import_row_id uuid, source_record_key text, reported_at timestamptz,
                        content_raw text, content_masked text, checksum text
                    )
                )
                UPDATE import_row AS row
                SET commit_status = 'COMMITTED', feedback_id = feedback.feedback_id, committed_at = now()
                FROM rows
                INNER JOIN feedback
                  ON feedback.source_system = :source_system
                 AND feedback.source_record_key = rows.source_record_key
                WHERE row.import_row_id = rows.import_row_id
                  AND row.commit_status = 'PENDING'
                RETURNING row.import_row_id
            """),
            params,
        )
        return len(result.scalars().all())

    async def finish_execution(self, import_job_id: UUID, *, error_object_key: str | None) -> str:
        result = await self._session.execute(
            text("""
                SELECT total_rows, valid_rows, invalid_rows,
                    COUNT(*) FILTER (WHERE commit_status = 'COMMITTED') AS committed_rows,
                    COUNT(*) FILTER (WHERE commit_status = 'FAILED') AS failed_rows
                FROM import_job AS job
                LEFT JOIN import_row AS row ON row.import_job_id = job.import_job_id
                WHERE job.import_job_id = :import_job_id
                GROUP BY job.import_job_id
            """),
            {"import_job_id": import_job_id},
        )
        row = result.mappings().one()
        committed = int(row["committed_rows"] or 0)
        invalid = int(row["invalid_rows"] or 0)
        failed = int(row["failed_rows"] or 0)
        status = "COMPLETED" if not invalid and not failed else "PARTIAL" if committed else "FAILED"
        await self._session.execute(
            text("""
                UPDATE import_job
                SET status = :status, committed_rows = :committed_rows,
                    error_object_key = :error_object_key, completed_at = now(), version = version + 1
                WHERE import_job_id = :import_job_id
            """),
            {
                "import_job_id": import_job_id,
                "status": status,
                "committed_rows": committed,
                "error_object_key": error_object_key,
            },
        )
        return status

    async def error_report_rows(self, import_job_id: UUID) -> list[Mapping[str, Any]]:
        """Return only safe lineage/error columns — never source content."""
        result = await self._session.execute(
            text("""
                SELECT row.row_number, row.source_record_key, error.field_name,
                    error.error_code, error.message, error.severity
                FROM import_row AS row
                INNER JOIN import_row_error AS error ON error.import_row_id = row.import_row_id
                WHERE row.import_job_id = :import_job_id
                ORDER BY row.row_number, error.import_row_error_id
            """),
            {"import_job_id": import_job_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def mark_failed(self, import_job_id: UUID) -> None:
        await self._session.execute(
            text("""
                UPDATE import_job
                SET status = 'FAILED', completed_at = now(), version = version + 1
                WHERE import_job_id = :import_job_id AND status IN ('VALIDATING', 'PROCESSING', 'QUEUED')
            """),
            {"import_job_id": import_job_id},
        )


def _as_domain_job(row: Mapping[str, Any]) -> ImportJob:
    return ImportJob(
        import_job_id=row["import_job_id"], project_id=row["project_id"],
        source_system=row["source_system"], original_filename=row["original_filename"],
        object_key=row["object_key"], file_checksum=row["file_checksum"],
        file_size_bytes=int(row["file_size_bytes"]), content_type=row["content_type"],
        requested_by=row["requested_by"], correlation_id=row["correlation_id"],
        status=ImportJobStatus(row["status"]), version=int(row["version"]),
        total_rows=row["total_rows"], valid_rows=row["valid_rows"], invalid_rows=row["invalid_rows"],
        committed_rows=row["committed_rows"], created_at=row["created_at"],
        started_at=row["started_at"], completed_at=row["completed_at"],
    )


def _row_parameters(import_job_id: UUID, row: ImportRow) -> dict[str, Any]:
    return {
        "import_job_id": import_job_id, "row_number": row.row_number,
        "source_record_key": row.source_record_key, "idempotency_key": row.idempotency_key,
        "raw_row_json": json.dumps(row.raw_row, default=str),
        "normalized_row_json": json.dumps(row.normalized_row, default=str),
        "validation_status": row.validation_status, "commit_status": row.commit_status,
    }


def _error_parameters(import_row_id: UUID, error: ImportRowError) -> dict[str, Any]:
    return {
        "import_row_id": import_row_id, "field_name": error.field_name,
        "error_code": error.error_code, "message": error.message,
        "severity": error.severity, "metadata_json": json.dumps(error.metadata, default=str),
    }


def _commit_payload(job: ImportJob, rows: Iterable[PersistedImportRow]) -> list[dict[str, str]]:
    payload: list[dict[str, str]] = []
    for row in rows:
        normalized = row.normalized_row
        content = str(normalized.get("content") or "").strip()
        if not content:
            continue
        reported_at = _reported_at(normalized.get("reported_at"))
        source_record_key = row.source_record_key or f"import:{job.import_job_id}:{row.idempotency_key}"
        payload.append({
            "import_row_id": str(row.import_row_id), "source_record_key": source_record_key,
            "reported_at": reported_at.isoformat(), "content_raw": content,
            "content_masked": _mask_content(content),
            "checksum": hashlib.sha256(content.encode()).hexdigest(),
        })
    return payload


def _reported_at(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        parsed = datetime.now(timezone.utc)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _mask_content(value: str) -> str:
    """Minimal P0 display masking; raw text remains only in the privileged envelope."""
    import re

    value = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", value)
    return re.sub(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)", "[PHONE]", value)


def _batches[T](items: list[T], size: int) -> Iterable[list[T]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]
