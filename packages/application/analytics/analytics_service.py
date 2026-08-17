"""Application service that applies the shared analytics eligibility rule."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, Sequence
from uuid import UUID

from packages.domain.analytics.dto import SummaryDTO
from packages.domain.analytics.predicates import AnalyticsEligibilityItem, is_analytics_eligible
from packages.domain.shared.enums import OperationalSeverity, Sentiment


@dataclass(frozen=True, slots=True)
class AnalyticsFilters:
    """The shared P0 filter context passed to all analytics repository reads."""

    project_id: UUID
    date_from: date | None = None
    date_to: date | None = None
    source_system: str | None = None
    intake_channel_code: str | None = None
    affected_channel_code: str | None = None
    location_id: UUID | None = None
    location_scope: UUID | None = None
    customer_lifecycle_stage_code: str | None = None
    customer_lifecycle_step_code: str | None = None
    touchpoint_code: str | None = None
    service_request_step_code: str | None = None
    service_code: str | None = None
    issue_code: str | None = None
    sentiment: Sentiment | None = None
    operational_severity: OperationalSeverity | None = None


class AnalyticsItem(AnalyticsEligibilityItem, Protocol):
    """Repository row shape needed by the analytics summary use case."""

    feedback_item_id: UUID | str
    sentiment: Sentiment | str


class AnalyticsRepository(Protocol):
    """Port implemented by the governed analytics semantic-view repository."""

    async def list_items(self, filters: AnalyticsFilters) -> Sequence[AnalyticsItem]:
        """Return rows in the requested filter context from the semantic layer."""
        ...


class AnalyticsService:
    """Coordinates analytics reads without allowing ineligible rows into KPIs."""

    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    async def eligible_items(self, filters: AnalyticsFilters) -> list[AnalyticsItem]:
        """Load distinct eligible items under the requested filter context.

        A semantic view should already return one row per feedback item; this
        defensive de-duplication preserves BR-ANA-001 even if a later
        repository joins a multi-valued dimension such as affected channel.
        """
        items = await self._repository.list_items(filters)
        eligible_by_id: dict[str, AnalyticsItem] = {}
        for item in items:
            if is_analytics_eligible(item):
                eligible_by_id.setdefault(str(item.feedback_item_id), item)
        return list(eligible_by_id.values())

    async def get_summary(self, filters: AnalyticsFilters) -> SummaryDTO:
        """Calculate the summary from only eligible feedback-item records."""
        items = await self.eligible_items(filters)
        return SummaryDTO.from_sentiments(item.sentiment for item in items)
