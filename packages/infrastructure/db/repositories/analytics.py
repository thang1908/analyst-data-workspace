"""Async repository for the governed P0 analytics semantic view."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Sequence
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.analytics.analytics_service import AnalyticsFilters
from packages.domain.analytics.dto import BreakdownItemDTO, SummaryDTO, TrendPointDTO
from packages.domain.shared.enums import (
    AnalyticEligibility,
    ClassificationState,
    FeedbackItemStatus,
    Sentiment,
)
from packages.infrastructure.db.queries.analytics_queries import (
    ANALYTICS_VIEW,
    AFFECTED_CHANNEL_BREAKDOWN_SQL,
    BREAKDOWN_DIMENSIONS,
    BREAKDOWN_SQL,
    SUMMARY_SQL,
    TREND_SQL,
)

_VALID_GRAINS: Final = frozenset({"day", "week", "month"})

_FILTER_COLUMNS: Final = {
    "source_system": "source_system",
    "intake_channel_code": "intake_channel_code",
    "location_id": "location_id",
    "customer_lifecycle_stage_code": "customer_lifecycle_stage_code",
    "customer_lifecycle_step_code": "customer_lifecycle_step_code",
    "service_request_step_code": "service_request_step_code",
    "service_code": "service_code",
    "issue_code": "issue_code",
    "sentiment": "sentiment",
    "operational_severity": "operational_severity",
}


@dataclass(frozen=True, slots=True)
class AnalyticsItemRow:
    """Semantic-view row shaped for the task #24 application repository port."""

    feedback_item_id: UUID | str
    sentiment: Sentiment | str
    status: FeedbackItemStatus | str = FeedbackItemStatus.ACTIVE
    analytic_eligibility: AnalyticEligibility | str = AnalyticEligibility.INCLUDED
    current_decision_id: UUID | str | None = None
    classification_state: ClassificationState | str = ClassificationState.ACCEPTED


class AnalyticsRepository:
    """Execute analytics reads exclusively against ``analytics_feedback_item_v1``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(self, filters: AnalyticsFilters) -> SummaryDTO:
        """Return summary rates calculated with the BR-ANA-003 denominators."""
        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(SUMMARY_SQL.format(where_clause=where_clause)), params
        )
        row = result.mappings().one()
        return SummaryDTO(
            total=int(row["total"] or 0),
            csat_score=float(row["csat_score"] or 0.0),
            positive_rate=float(row["positive_rate"] or 0.0),
            negative_rate=float(row["negative_rate"] or 0.0),
            sentiment_unknown_rate=float(row["sentiment_unknown_rate"] or 0.0),
        )

    async def get_trend(
        self,
        filters: AnalyticsFilters,
        grain: str,
    ) -> list[TrendPointDTO]:
        """Return distinct eligible item volume grouped by day, week, or month."""
        if grain not in _VALID_GRAINS:
            raise ValueError("grain must be one of: day, week, month")
        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(TREND_SQL.format(where_clause=where_clause)),
            {**params, "grain": grain},
        )
        return [
            TrendPointDTO(time_bucket=row["time_bucket"], volume=int(row["volume"]))
            for row in result.mappings().all()
        ]

    async def get_breakdown(
        self,
        filters: AnalyticsFilters,
        dimension: str,
    ) -> list[BreakdownItemDTO]:
        """Return a safe, dimension-specific breakdown from the semantic view."""
        if dimension == "affected_channel":
            return await self._get_affected_channel_breakdown(filters)
        try:
            dimension_column = BREAKDOWN_DIMENSIONS[dimension]
        except KeyError as exc:
            supported = ", ".join(
                key for key in BREAKDOWN_DIMENSIONS if key != "stage"
            )
            raise ValueError(f"unsupported analytics dimension: {dimension}. Use: {supported}") from exc

        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(
                BREAKDOWN_SQL.format(
                    dimension_column=dimension_column,
                    where_clause=where_clause,
                )
            ),
            params,
        )
        return [
            BreakdownItemDTO(
                dimension_key=str(row["dimension_key"]),
                count=int(row["count"]),
                percentage=float(row["percentage"]),
            )
            for row in result.mappings().all()
        ]

    async def _get_affected_channel_breakdown(
        self, filters: AnalyticsFilters
    ) -> list[BreakdownItemDTO]:
        """Break down an item's zero-to-many affected channels at item grain."""
        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(AFFECTED_CHANNEL_BREAKDOWN_SQL.format(where_clause=where_clause)),
            params,
        )
        return [
            BreakdownItemDTO(
                dimension_key=str(row["dimension_key"]),
                count=int(row["count"]),
                percentage=float(row["percentage"]),
            )
            for row in result.mappings().all()
        ]

    async def list_items(self, filters: AnalyticsFilters) -> Sequence[AnalyticsItemRow]:
        """Implement the task #24 application port using the same filter context.

        The view has already applied the central eligibility predicate.  Static
        values for the predicate-only fields let the application layer retain
        its defensive eligibility check without reading raw tables.
        """
        where_clause, params = self._filter_query(filters)
        items_sql = f"""
        SELECT
            feedback_item_id,
            sentiment,
            'ACTIVE' AS status,
            'INCLUDED' AS analytic_eligibility,
            current_decision_id,
            classification_state
        FROM {ANALYTICS_VIEW}
        WHERE {where_clause}
        """
        result = await self._session.execute(text(items_sql), params)
        return [
            AnalyticsItemRow(
                feedback_item_id=row["feedback_item_id"],
                sentiment=row["sentiment"],
                current_decision_id=row["current_decision_id"],
                classification_state=row["classification_state"],
            )
            for row in result.mappings().all()
        ]

    @staticmethod
    def _filter_query(filters: AnalyticsFilters) -> tuple[str, dict[str, Any]]:
        """Compile only semantic-view backed filters into bound SQL parameters."""
        clauses = ["project_id = :project_id"]
        params: dict[str, Any] = {"project_id": filters.project_id}

        if filters.date_from is not None:
            clauses.append("reported_at >= :date_from")
            params["date_from"] = filters.date_from
        if filters.date_to is not None:
            clauses.append("reported_at < (:date_to + INTERVAL '1 day')")
            params["date_to"] = filters.date_to
        if filters.affected_channel_code is not None:
            clauses.append(":affected_channel_code = ANY(affected_channel_codes)")
            params["affected_channel_code"] = filters.affected_channel_code
        if filters.location_scope is not None:
            clauses.append("""
            location_id IN (
                WITH RECURSIVE location_scope_tree AS (
                    SELECT location_id
                    FROM location
                    WHERE location_id = :location_scope
                    UNION
                    SELECT child.location_id
                    FROM location AS child
                    INNER JOIN location_scope_tree AS parent
                        ON child.parent_location_id = parent.location_id
                )
                SELECT location_id FROM location_scope_tree
            )
            """)
            params["location_scope"] = filters.location_scope

        for field_name, column_name in _FILTER_COLUMNS.items():
            value = getattr(filters, field_name)
            if value is not None:
                clauses.append(f"{column_name} = :{field_name}")
                params[field_name] = str(value)
        return " AND ".join(clauses), params
