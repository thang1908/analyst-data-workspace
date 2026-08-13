"""Pure mapping, row-validation, and deterministic idempotency rules."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Iterable, Mapping

from packages.domain.import_pipeline.entities import ImportRow, ImportRowError
from packages.domain.import_pipeline.exceptions import ImportSchemaError

_REQUIRED_CANONICAL_FIELDS = frozenset({"content"})
_SUPPORTED_CANONICAL_FIELDS = frozenset({
    "source_record_key", "reported_at", "content", "project", "intake_channel", "affected_channels", "location",
})


def validate_mapping(mapping: Mapping[str, str]) -> None:
    """Reject blocking schema errors before a worker validates any row."""
    if not mapping:
        raise ImportSchemaError("A column mapping is required before validation.")
    unsupported = sorted(set(mapping) - _SUPPORTED_CANONICAL_FIELDS)
    if unsupported:
        raise ImportSchemaError("Mapping contains unsupported canonical fields.", {"fields": unsupported})
    missing = sorted(_REQUIRED_CANONICAL_FIELDS - set(mapping))
    if missing:
        raise ImportSchemaError("Mapping is missing required fields.", {"fields": missing})
    source_columns = list(mapping.values())
    if any(not column.strip() for column in source_columns):
        raise ImportSchemaError("Mapping cannot reference an empty source column.")
    if len(source_columns) != len(set(source_columns)):
        raise ImportSchemaError("Each source column can map to one canonical field only.")


def idempotency_key(source_system: str, normalized_row: Mapping[str, Any]) -> str:
    """Return a stable row identity even when a source lacks a record key."""
    source_record_key = str(normalized_row.get("source_record_key") or "").strip()
    identity = source_record_key or json.dumps(normalized_row, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(f"{source_system}:{identity}".encode()).hexdigest()


def validate_rows(
    *,
    source_system: str,
    mapping: Mapping[str, str],
    raw_rows: Iterable[Mapping[str, Any]],
    existing_source_record_keys: frozenset[str] = frozenset(),
) -> list[ImportRow]:
    """Validate every supplied row and retain an explicit outcome for each one."""
    validate_mapping(mapping)
    seen_idempotency_keys: set[str] = set()
    validated_rows: list[ImportRow] = []

    for row_number, raw_row in enumerate(raw_rows, start=1):
        normalized = {canonical: raw_row.get(source) for canonical, source in mapping.items()}
        source_record_key = _nonempty_text(normalized.get("source_record_key"))
        errors: list[ImportRowError] = []
        content = _nonempty_text(normalized.get("content"))
        if content is None:
            errors.append(ImportRowError("REQUIRED_FIELD", "Feedback content is required.", "content"))

        event_time_inferred = normalized.get("reported_at") in (None, "")
        if not event_time_inferred and _parse_datetime(normalized["reported_at"]) is None:
            errors.append(ImportRowError("INVALID_DATETIME", "reported_at must be an ISO-8601 date or datetime.", "reported_at"))

        key = idempotency_key(source_system, normalized)
        if key in seen_idempotency_keys:
            errors.append(ImportRowError("DUPLICATE_IN_FILE", "Duplicate row identity in this import file."))
        elif source_record_key is not None and source_record_key in existing_source_record_keys:
            errors.append(ImportRowError("DUPLICATE_SOURCE_RECORD", "Source record was already imported."))
        seen_idempotency_keys.add(key)

        validated_rows.append(
            ImportRow(
                row_number=row_number,
                idempotency_key=key,
                raw_row=dict(raw_row),
                normalized_row=normalized,
                source_record_key=source_record_key,
                validation_status="INVALID" if errors else "VALID",
                errors=tuple(errors),
                event_time_inferred=event_time_inferred,
            )
        )
    return validated_rows


def _nonempty_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
