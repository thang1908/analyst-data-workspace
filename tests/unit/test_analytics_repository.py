"""Unit tests for task #25 governed analytics SQL repository."""
from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from packages.application.analytics.analytics_service import AnalyticsFilters
from packages.domain.analytics.dto import SummaryDTO
from packages.domain.shared.enums import OperationalSeverity, Sentiment
from packages.infrastructure.db.repositories.analytics import AnalyticsRepository


def _session_returning(
    rows: list[dict[str, object]],
    *,
    one: dict[str, object] | None = None,
) -> AsyncMock:
    result = MagicMock()
    mappings = result.mappings.return_value
    mappings.all.return_value = rows
    mappings.one.return_value = one if one is not None else (rows[0] if rows else {})
    session = AsyncMock()
    session.execute = AsyncMock(return_value=result)
    return session


@pytest.mark.asyncio
async def test_summary_uses_governed_view_distinct_item_counts_and_known_sentiment_rates() -> None:
    row = {
        "total": 4,
        "csat_score": 1 / 3,
        "positive_rate": 1 / 3,
        "negative_rate": 1 / 3,
        "sentiment_unknown_rate": 0.25,
    }
    session = _session_returning([], one=row)
    repository = AnalyticsRepository(session)

    summary = await repository.get_summary(AnalyticsFilters(project_id=uuid4()))

    assert summary == SummaryDTO(
        total=4,
        csat_score=pytest.approx(1 / 3),
        positive_rate=pytest.approx(1 / 3),
        negative_rate=pytest.approx(1 / 3),
        sentiment_unknown_rate=0.25,
    )
    statement = session.execute.await_args.args[0].text
    assert "analytics_feedback_item_v1" in statement
    assert "COUNT(DISTINCT item.feedback_item_id)" in statement
    assert "sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')" in statement


@pytest.mark.asyncio
async def test_summary_binds_supported_filter_context() -> None:
    session = _session_returning(
        [],
        one={
            "total": 0,
            "csat_score": 0.0,
            "positive_rate": 0.0,
            "negative_rate": 0.0,
            "sentiment_unknown_rate": 0.0,
        },
    )
    filters = AnalyticsFilters(
        project_id=uuid4(),
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        source_system="resident_app",
        intake_channel_code="CH-APP",
        affected_channel_code="CH-HOTLINE",
        location_id=uuid4(),
        location_scope=uuid4(),
        customer_lifecycle_stage_code="RES",
        customer_lifecycle_step_code="RES-03",
        service_request_step_code="SRV-05",
        service_code="SV-07",
        issue_code="IS-07-01",
        sentiment=Sentiment.NEGATIVE,
        operational_severity=OperationalSeverity.SEV_2,
    )

    await AnalyticsRepository(session).get_summary(filters)

    statement, params = session.execute.await_args.args
    assert "reported_at >= :date_from" in statement.text
    assert "reported_at < (:date_to + INTERVAL '1 day')" in statement.text
    assert "customer_lifecycle_stage_code = :customer_lifecycle_stage_code" in statement.text
    assert "intake_channel_code = :intake_channel_code" in statement.text
    assert ":affected_channel_code = ANY(item.affected_channel_codes)" in statement.text
    assert "WITH RECURSIVE location_scope_tree" in statement.text
    assert params["sentiment"] == "NEGATIVE"
    assert params["operational_severity"] == "SEV-2"


@pytest.mark.asyncio
async def test_trend_groups_by_requested_postgres_grain() -> None:
    bucket = datetime(2026, 8, 10, tzinfo=timezone.utc)
    session = _session_returning([{"time_bucket": bucket, "volume": 12}])

    trend = await AnalyticsRepository(session).get_trend(
        AnalyticsFilters(project_id=uuid4()), "week"
    )

    assert trend[0].time_bucket == bucket
    assert trend[0].volume == 12
    statement, params = session.execute.await_args.args
    assert "DATE_TRUNC(:grain, item.reported_at)" in statement.text
    assert params["grain"] == "week"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dimension", "expected_column"),
    [
        ("service", "service_code"),
        ("issue", "issue_code"),
        ("journey_stage", "customer_lifecycle_stage_code"),
    ],
)
async def test_breakdown_uses_a_whitelisted_dimension_column(
    dimension: str,
    expected_column: str,
) -> None:
    session = _session_returning(
        [{"dimension_key": "SV-07", "count": 3, "percentage": 0.75}]
    )

    breakdown = await AnalyticsRepository(session).get_breakdown(
        AnalyticsFilters(project_id=uuid4()), dimension
    )

    assert breakdown[0].percentage == 0.75
    statement = session.execute.await_args.args[0].text
    assert f"COALESCE(item.{expected_column}, 'UNKNOWN')" in statement
    assert "negative_rate" in statement
    assert "active_hotspots" in statement
    assert "COUNT(DISTINCT item.feedback_item_id)" in statement


@pytest.mark.asyncio
async def test_repository_rejects_invalid_grain_and_dimension() -> None:
    session = _session_returning([])
    repository = AnalyticsRepository(session)
    filters = AnalyticsFilters(project_id=uuid4())

    with pytest.raises(ValueError, match="grain must be one of"):
        await repository.get_trend(filters, "year")
    with pytest.raises(ValueError, match="unsupported analytics dimension"):
        await repository.get_breakdown(filters, "persona")
    session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_affected_channel_breakdown_unnests_codes_from_the_semantic_view() -> None:
    session = _session_returning(
        [{"dimension_key": "CH-HOTLINE", "count": 3, "percentage": 1.0}]
    )

    breakdown = await AnalyticsRepository(session).get_breakdown(
        AnalyticsFilters(project_id=uuid4(), affected_channel_code="CH-HOTLINE"),
        "affected_channel",
    )

    assert breakdown[0].dimension_key == "CH-HOTLINE"
    statement, params = session.execute.await_args.args
    assert "UNNEST(item.affected_channel_codes)" in statement.text
    assert ":affected_channel_code = ANY(item.affected_channel_codes)" in statement.text
    assert params["affected_channel_code"] == "CH-HOTLINE"


@pytest.mark.asyncio
async def test_list_items_adapts_semantic_view_rows_to_the_application_port() -> None:
    item_id = uuid4()
    decision_id = uuid4()
    session = _session_returning(
        [
            {
                "feedback_item_id": item_id,
                "sentiment": "NEGATIVE",
                "current_decision_id": decision_id,
                "classification_state": "ACCEPTED",
            }
        ]
    )

    items = await AnalyticsRepository(session).list_items(
        AnalyticsFilters(project_id=uuid4())
    )

    assert items[0].feedback_item_id == item_id
    assert items[0].sentiment == "NEGATIVE"
    assert items[0].current_decision_id == decision_id
    statement = session.execute.await_args.args[0].text
    assert "'ACTIVE' AS status" in statement
    assert "'INCLUDED' AS analytic_eligibility" in statement
