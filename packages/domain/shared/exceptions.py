from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DomainRuleViolationError(DomainError):
    """Raised when a core domain rule or invariant is violated."""

    def __init__(
        self,
        message: str,
        field_errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            message,
            code="DOMAIN_RULE_VIOLATION",
            details={"field_errors": field_errors or []},
        )


class VersionConflictError(DomainError):
    """Raised when an optimistic concurrency check fails."""

    def __init__(self, message: str = "Stale version in optimistic concurrency check.") -> None:
        super().__init__(message, code="VERSION_CONFLICT")


class IdempotencyConflictError(DomainError):
    """Raised when a request reuses an Idempotency-Key with conflicting payload."""

    def __init__(self, message: str = "Reused idempotency key with conflicting payload.") -> None:
        super().__init__(message, code="IDEMPOTENCY_CONFLICT")


class NotFoundError(DomainError):
    """Raised when a requested domain resource is not found."""

    def __init__(self, resource: str, resource_id: Any) -> None:
        super().__init__(f"{resource} with id '{resource_id}' was not found.", code="NOT_FOUND")


class ForbiddenError(DomainError):
    """Raised when an operation violates permission boundaries."""

    def __init__(
        self,
        message: str = "Access denied due to insufficient privilege or scope mismatch.",
    ) -> None:
        super().__init__(message, code="FORBIDDEN")


class ValidationError(DomainError):
    """Raised when request payload or data validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", details=details)
