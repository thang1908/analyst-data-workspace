"""Import-pipeline specific domain errors."""
from __future__ import annotations

from packages.domain.shared.exceptions import DomainRuleViolationError, ValidationError
from packages.domain.shared.enums import ImportJobStatus


class InvalidImportTransitionError(DomainRuleViolationError):
    """Raised when an import job attempts to bypass its lifecycle."""

    def __init__(self, current: ImportJobStatus, target: ImportJobStatus) -> None:
        super().__init__(
            f"Import job cannot transition from {current} to {target}.",
            field_errors=[{"field": "status", "code": "INVALID_IMPORT_TRANSITION"}],
        )


class ImportSchemaError(ValidationError):
    """A blocking file/schema error that must fail the import job."""

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(message, details)
