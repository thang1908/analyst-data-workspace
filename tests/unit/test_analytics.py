"""Unit tests for task #24 analytics domain and application rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

import pytest

from packages.application.analytics.analytics_service import (
    AnalyticsFilters,
    AnalyticsService,
)
from packages.domain.analytics.dto import BreakdownItemDTO, SummaryDTO
from packages.domain.analytics.predicates import is_analytics_eligible
from packages.domain.shared.enums import (
    AnalyticEligibility,
    ClassificationState,
    FeedbackItemStatus,
    OperationalSeverity,
    Sentiment,
)


@dataclass(frozen=True)
class AnalyticsTestItem:
    feedback_item_id: UUID = field(default_factory=uuid4)
    status: FeedbackItemStatus | str = FeedbackItemStatus.ACTIVE
    analytic_eligibility: AnalyticEligibility | str = AnalyticEligibility.INCLUDED
    current_decision_id: UUID | None = uuid4()
    classification_state: ClassificationState | str = ClassificationState.ACCEPTED
    sentiment: Sentiment | str = Sentiment.NEUTRAL


@pytest.mark.parametrize(
    "item",
    [
        AnalyticsTestItem(),
        AnalyticsTestItem(
            status="ACTIVE",
            analytic_eligibility="INCLUDED",
            classification_state="ACCEPTED",
        ),
    ],
)
def test_analytics_eligibility_accepts_active_included_accepted_items(
    item: AnalyticsTestItem,
) -> None:
    assert is_analytics_eligible(item)


@pytest.mark.parametrize(
    "item",
    [
        AnalyticsTestItem(status=FeedbackItemStatus.RETIRED),
        AnalyticsTestItem(analytic_eligibility=AnalyticEligibility.EXCLUDED),
        AnalyticsTestItem(current_decision_id=None),
        AnalyticsTestItem(classification_state=ClassificationState.PENDING_REVIEW),
    ],
)
def test_analytics_eligibility_rejects_invalid_items(item: AnalyticsTestItem) -> None:
    assert not is_analytics_eligible(item)


def test_summary_uses_known_sentiment_as_the_rate_denominator() -> None:
    summary = SummaryDTO.from_sentiments(
        [Sentiment.POSITIVE, Sentiment.NEGATIVE, Sentiment.NEUTRAL, Sentiment.UNKNOWN]
    )

    assert summary.total == 4
    assert summary.csat_score == pytest.approx(1 / 3)
    assert summary.positive_rate == pytest.approx(1 / 3)
    assert summary.negative_rate == pytest.approx(1 / 3)
    assert summary.sentiment_unknown_rate == 0.25
    assert summary.unknown_rate == 0.25


def test_summary_handles_an_unknown_only_population() -> None:
    summary = SummaryDTO.from_sentiments([Sentiment.UNKNOWN])

    assert summary.total == 1
    assert summary.csat_score == 0.0
    assert summary.positive_rate == 0.0
    assert summary.negative_rate == 0.0
    assert summary.sentiment_unknown_rate == 1.0


def test_summary_handles_an_empty_population() -> None:
    summary = SummaryDTO.from_sentiments([])

    assert summary.total == 0
    assert summary.csat_score == 0.0
    assert summary.positive_rate == 0.0
    assert summary.negative_rate == 0.0
    assert summary.sentiment_unknown_rate == 0.0


def test_breakdown_calculates_percentage_and_guards_invalid_counts() -> None:
    breakdown = BreakdownItemDTO.from_count(
        dimension_key="SV-07", count=3, total=12
    )

    assert breakdown.percentage == 0.25
    with pytest.raises(ValueError, match="must not be negative"):
        BreakdownItemDTO.from_count(dimension_key="SV-07", count=-1, total=12)


class StubAnalyticsRepository:
    def __init__(self, items: list[AnalyticsTestItem]) -> None:
        self.items = items
        self.received_filters: AnalyticsFilters | None = None

    async def list_items(self, filters: AnalyticsFilters) -> list[AnalyticsTestItem]:
        self.received_filters = filters
        return self.items


@pytest.mark.asyncio
async def test_service_filters_ineligible_items_before_calculating_summary() -> None:
    repository = StubAnalyticsRepository(
        [
            AnalyticsTestItem(sentiment=Sentiment.POSITIVE),
            AnalyticsTestItem(
                sentiment=Sentiment.NEGATIVE,
                analytic_eligibility=AnalyticEligibility.EXCLUDED,
            ),
            AnalyticsTestItem(sentiment=Sentiment.NEGATIVE, current_decision_id=None),
        ]
    )
    filters = AnalyticsFilters(project_id=uuid4(), date_from=date(2026, 8, 1))

    summary = await AnalyticsService(repository).get_summary(filters)

    assert repository.received_filters == filters
    assert summary == SummaryDTO(
        total=1,
        csat_score=1.0,
        positive_rate=1.0,
        negative_rate=0.0,
        sentiment_unknown_rate=0.0,
    )


@pytest.mark.asyncio
async def test_service_counts_each_eligible_feedback_item_once() -> None:
    item_id = uuid4()
    repository = StubAnalyticsRepository(
        [
            AnalyticsTestItem(feedback_item_id=item_id, sentiment=Sentiment.POSITIVE),
            AnalyticsTestItem(feedback_item_id=item_id, sentiment=Sentiment.NEGATIVE),
        ]
    )

    summary = await AnalyticsService(repository).get_summary(
        AnalyticsFilters(project_id=uuid4())
    )

    assert summary.total == 1
    assert summary.positive_rate == 1.0


def test_analytics_filters_implement_the_complete_shared_p0_contract() -> None:
    location_id = uuid4()
    filters = AnalyticsFilters(
        project_id=uuid4(),
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        source_system="resident_app",
        intake_channel_code="APP",
        affected_channel_code="ELEVATOR",
        location_id=location_id,
    location_scope=location_id,
        customer_lifecycle_stage_code="RES",
        customer_lifecycle_step_code="RES-03",
        service_request_step_code="SRV-05",
        service_code="SV-07",
        issue_code="IS-07-01",
        sentiment=Sentiment.NEGATIVE,
        operational_severity=OperationalSeverity.SEV_2,
    )

    assert filters.location_id == location_id
    assert filters.customer_lifecycle_stage_code == "RES"
    assert filters.customer_lifecycle_step_code == "RES-03"
    assert filters.issue_code == "IS-07-01"
    assert filters.operational_severity == OperationalSeverity.SEV_2
