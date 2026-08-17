"""Exceptions for Hotspot domain."""
from __future__ import annotations

from packages.domain.shared.exceptions import DomainError


class HotspotDomainError(DomainError):
    """Base exception for all hotspot domain errors."""


class InvalidStateTransitionError(HotspotDomainError):
    """Raised when a requested hotspot state transition is not allowed."""


class HotspotNotFoundError(HotspotDomainError):
    """Raised when a hotspot cannot be found."""


class ConcurrencyConflictError(HotspotDomainError):
    """Raised when optimistic concurrency check fails."""
