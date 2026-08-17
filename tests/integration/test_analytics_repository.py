"""PostgreSQL integration tests for the governed analytics repository.

Run explicitly against the local database after migrations are applied:

    RUN_ANALYTICS_INTEGRATION_TESTS=1 uv run --group dev \
        pytest tests/integration/test_analytics_repository.py -v

Every test opens a transaction and rolls it back, so no fixture data remains
in the developer database.
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from time import perf_counter
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.analytics.analytics_service import AnalyticsFilters
from packages.infrastructure.db.repositories.analytics import AnalyticsRepository
from packages.infrastructure.db.session import engine

if os.getenv("RUN_ANALYTICS_INTEGRATION_TESTS") != "1":
    pytestmark = pytest.mark.skip(
        reason="set RUN_ANALYTICS_INTEGRATION_TESTS=1 to use local PostgreSQL"
    )


_REFERENCE_IDS_SQL = text("""
SELECT
    (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
        AS taxonomy_release_id,
    (SELECT customer_lifecycle_stage_id FROM customer_lifecycle_stage
     WHERE taxonomy_release_id = (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
       AND stage_code = 'RES') AS stage_id,
    (SELECT customer_lifecycle_step_id FROM customer_lifecycle_step
     WHERE taxonomy_release_id = (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
       AND step_code = 'RES-03') AS lifecycle_step_id,
    (SELECT service_request_step_id FROM service_request_step
     WHERE taxonomy_release_id = (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
       AND step_code = 'SRV-05') AS service_request_step_id,
    (SELECT service_id FROM service
     WHERE taxonomy_release_id = (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
       AND service_code = 'SV-07') AS service_id,
    (SELECT issue_id FROM issue
     WHERE taxonomy_release_id = (SELECT taxonomy_release_id FROM taxonomy_release WHERE version = '3.0.1')
       AND issue_code = 'IS-07-01') AS issue_id,
    (SELECT interaction_channel_id FROM interaction_channel
     WHERE channel_code = 'CH-APP') AS intake_channel_id,
    (SELECT interaction_channel_id FROM interaction_channel
     WHERE channel_code = 'CH-HOTLINE') AS affected_channel_id
""")

_INSERT_LOCATION_SQL = text("""
INSERT INTO location (
    location_id, project_id, parent_location_id, location_code, location_type,
    name, path_code
) VALUES (
    :location_id, :project_id, :parent_location_id, :location_code,
    :location_type, :name, :path_code
)
""")

_INSERT_FEEDBACK_SQL = text("""
INSERT INTO feedback (
    feedback_id, project_id, source_system, source_record_key, intake_channel_id, reported_at,
    content_raw, content_masked, raw_content_checksum
) VALUES (
    :feedback_id, :project_id, 'integration-test', :source_record_key, :intake_channel_id, :reported_at,
    'Integration test feedback', 'Integration test feedback', :checksum
)
""")

_INSERT_ITEM_SQL = text("""
INSERT INTO feedback_item (
    feedback_item_id, feedback_id, item_index, item_text_masked, location_id, status,
    analytic_eligibility
) VALUES (
    :feedback_item_id, :feedback_id, 1, 'Integration test item', :location_id, 'ACTIVE', 'INCLUDED'
)
""")

_INSERT_AFFECTED_CHANNEL_SQL = text("""
INSERT INTO feedback_item_affected_channel (
    feedback_item_id, interaction_channel_id
) VALUES (:feedback_item_id, :affected_channel_id)
""")

_INSERT_DECISION_SQL = text("""
INSERT INTO classification_decision (
    classification_decision_id, feedback_item_id, decision_version,
    taxonomy_release_id, customer_lifecycle_value_status,
    customer_lifecycle_step_id, service_request_value_status,
    service_request_step_id, primary_service_value_status, primary_service_id,
    issue_value_status, issue_id, sentiment, operational_severity,
    cause_determination_status, classification_state, decision_source,
    decided_by, decided_at
) VALUES (
    :decision_id, :feedback_item_id, 1,
    :taxonomy_release_id, 'KNOWN', :lifecycle_step_id, 'KNOWN',
    :service_request_step_id, 'KNOWN', :service_id, 'KNOWN', :issue_id,
    :sentiment, 'SEV-2', 'NOT_ASSESSED', 'ACCEPTED', 'SOURCE_TRUSTED',
    :actor_id, :decided_at
)
""")

_INSERT_CURRENT_SQL = text("""
INSERT INTO classification_current (
    feedback_item_id, current_decision_id, current_decision_version,
    taxonomy_release_id, customer_lifecycle_value_status,
    customer_lifecycle_stage_id, customer_lifecycle_step_id,
    service_request_value_status, service_request_step_id,
    primary_service_value_status, primary_service_id, issue_value_status,
    issue_id, sentiment, operational_severity, cause_determination_status,
    classification_state, last_decision_at, projection_version
) VALUES (
    :feedback_item_id, :decision_id, 1,
    :taxonomy_release_id, 'KNOWN', :stage_id, :lifecycle_step_id,
    'KNOWN', :service_request_step_id, 'KNOWN', :service_id, 'KNOWN', :issue_id,
    :sentiment, 'SEV-2', 'NOT_ASSESSED', 'ACCEPTED', :decided_at, 1
)
""")


async def _seed_eligible_items(
    session: AsyncSession,
    *,
    project_id: UUID,
) -> UUID:
    reference_ids = (await session.execute(_REFERENCE_IDS_SQL)).mappings().one()
    assert all(reference_ids.values()), "published taxonomy 3.0.1 seed data is required"

    scope_location_id = uuid4()
    item_location_id = uuid4()
    await session.execute(
        _INSERT_LOCATION_SQL,
        {
            "location_id": scope_location_id,
            "project_id": project_id,
            "parent_location_id": None,
            "location_code": "INT-ROOT",
            "location_type": "BUILDING",
            "name": "Integration root",
            "path_code": "INT-ROOT",
        },
    )
    await session.execute(
        _INSERT_LOCATION_SQL,
        {
            "location_id": item_location_id,
            "project_id": project_id,
            "parent_location_id": scope_location_id,
            "location_code": "INT-CHILD",
            "location_type": "FLOOR",
            "name": "Integration child",
            "path_code": "INT-ROOT/INT-CHILD",
        },
    )

    reported_at = datetime(2026, 8, 10, 9, tzinfo=timezone.utc)
    for offset, sentiment in enumerate(("POSITIVE", "NEGATIVE", "NEUTRAL", "UNKNOWN")):
        feedback_id = uuid4()
        feedback_item_id = uuid4()
        decision_id = uuid4()
        timestamp = reported_at + timedelta(days=offset // 2)
        values = {
            **reference_ids,
            "project_id": project_id,
            "feedback_id": feedback_id,
            "feedback_item_id": feedback_item_id,
            "decision_id": decision_id,
            "source_record_key": str(feedback_id),
            "checksum": f"analytics-integration-{feedback_id}",
            "reported_at": timestamp,
            "decided_at": timestamp,
            "actor_id": uuid4(),
            "sentiment": sentiment,
            "location_id": item_location_id,
        }
        await session.execute(_INSERT_FEEDBACK_SQL, values)
        await session.execute(_INSERT_ITEM_SQL, values)
        await session.execute(_INSERT_AFFECTED_CHANNEL_SQL, values)
        await session.execute(_INSERT_DECISION_SQL, values)
        await session.execute(_INSERT_CURRENT_SQL, values)
    return scope_location_id


@pytest.mark.asyncio
async def test_analytics_repository_queries_real_postgres_under_100ms() -> None:
    """Execute summary, trend, and breakdown through the migrated semantic view."""
    project_id = uuid4()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            location_scope_id = await _seed_eligible_items(session, project_id=project_id)
            repository = AnalyticsRepository(session)
            filters = AnalyticsFilters(
                project_id=project_id,
                date_from=date(2026, 8, 10),
                date_to=date(2026, 8, 11),
                intake_channel_code="CH-APP",
                affected_channel_code="CH-HOTLINE",
                location_scope=location_scope_id,
                service_code="SV-07",
                customer_lifecycle_stage_code="RES",
            )

            started_at = perf_counter()
            summary = await repository.get_summary(filters)
            summary_duration = perf_counter() - started_at

            assert summary.total == 4
            assert summary.positive_rate == pytest.approx(1 / 3)
            assert summary.negative_rate == pytest.approx(1 / 3)
            assert summary.sentiment_unknown_rate == 0.25
            assert summary_duration < 0.1

            direct_location_summary = await repository.get_summary(
                AnalyticsFilters(project_id=project_id, location_id=location_scope_id)
            )
            assert direct_location_summary.total == 0

            started_at = perf_counter()
            trend = await repository.get_trend(filters, grain="day")
            trend_duration = perf_counter() - started_at

            assert [(point.time_bucket.date(), point.volume) for point in trend] == [
                (date(2026, 8, 10), 2),
                (date(2026, 8, 11), 2),
            ]
            assert trend_duration < 0.1

            for dimension, expected_key in (
                ("service", "SV-07"),
                ("issue", "IS-07-01"),
                ("journey_stage", "RES"),
                ("intake_channel", "CH-APP"),
                ("affected_channel", "CH-HOTLINE"),
            ):
                started_at = perf_counter()
                breakdown = await repository.get_breakdown(filters, dimension)
                breakdown_duration = perf_counter() - started_at

                assert [(item.dimension_key, item.count, item.percentage) for item in breakdown] == [
                    (expected_key, 4, 1.0)
                ]
                assert breakdown_duration < 0.1

            filter_options = await repository.get_filter_options(
                AnalyticsFilters(project_id=project_id)
            )
            # Only RES feedback was seeded, but the published taxonomy remains
            # available to keep the UI structure stable at zero volume.
            assert len(filter_options["journey_stages"]) == 6
            assert len(filter_options["journey_steps"]) == 36
            assert {option.code for option in filter_options["journey_stages"]} >= {"A", "RES", "OPS"}
            assert next(option.name for option in filter_options["journey_steps"] if option.code == "RES-03") == "Ra vào & di chuyển"
            assert next(option.name for option in filter_options["services"] if option.code == "SV-07") == "Kỹ thuật & tài sản chung"
            assert next(option.name for option in filter_options["issues"] if option.code == "IS-07-01") == "Hệ thống suy giảm"
        finally:
            await session.close()
            await transaction.rollback()
