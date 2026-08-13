"""Shared eligibility rules for every P0 analytics metric."""
from __future__ import annotations

from typing import Protocol, TypeAlias
from uuid import UUID

from packages.domain.shared.enums import (
    AnalyticEligibility,
    ClassificationState,
    FeedbackItemStatus,
)

EnumOrString: TypeAlias = str | AnalyticEligibility | ClassificationState | FeedbackItemStatus


class AnalyticsEligibilityItem(Protocol):
    """Minimum projection fields required to decide analytics eligibility.

    The protocol deliberately does not depend on an ORM model.  It allows the
    semantic SQL view, a repository row DTO, and a future FeedbackItem entity
    to use the exact same central predicate.
    """

    status: FeedbackItemStatus | str
    analytic_eligibility: AnalyticEligibility | str
    current_decision_id: UUID | str | None
    classification_state: ClassificationState | str


def _value(value: EnumOrString) -> str:
    """Return a stable string for enum values and plain repository values."""
    return str(value)


def is_analytics_eligible(item: AnalyticsEligibilityItem) -> bool:
    """Return whether *item* belongs to the P0 analytics denominator.

    This mirrors the central predicate in ``analytics_feedback_item_v1`` and
    implements BR-ANA-002: only active, explicitly included items with an
    accepted current decision may be used by standard analytics.  Unreviewed
    predictions, excluded duplicates, split parents, and retired items fail
    at least one of these checks.
    """
    return (
        _value(item.status) == FeedbackItemStatus.ACTIVE
        and _value(item.analytic_eligibility) == AnalyticEligibility.INCLUDED
        and item.current_decision_id is not None
        and _value(item.classification_state) == ClassificationState.ACCEPTED
    )
