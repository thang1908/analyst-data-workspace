"""Domain-specific errors for immutable feedback envelopes."""
from __future__ import annotations

from packages.domain.shared.exceptions import DomainRuleViolationError


class FeedbackDomainError(DomainRuleViolationError):
    """Raised when a feedback aggregate would violate a feedback rule."""

