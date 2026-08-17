"""Async repository for the governed P0 analytics semantic view."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Sequence
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.application.analytics.analytics_service import AnalyticsFilters
from packages.domain.analytics.dto import BreakdownItemDTO, FilterOptionDTO, SummaryDTO, TrendPointDTO
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
    FILTER_OPTIONS_SQL,
    SUMMARY_SQL,
    TAXONOMY_FILTER_OPTIONS_SQL,
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
            active_hotspots=int(row.get("active_hotspots") or 0),
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
            TrendPointDTO(
                time_bucket=row["time_bucket"],
                volume=int(row["volume"]),
                negative_rate=float(row.get("negative_rate") or 0.0),
                unknown_rate=float(row.get("unknown_rate") or 0.0),
                active_hotspots=int(row.get("active_hotspots") or 0),
            )
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
            dimension_definition = BREAKDOWN_DIMENSIONS[dimension]
        except KeyError as exc:
            supported = ", ".join(
                key for key in BREAKDOWN_DIMENSIONS if key != "stage"
            )
            raise ValueError(f"unsupported analytics dimension: {dimension}. Use: {supported}") from exc

        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(
                BREAKDOWN_SQL.format(
                    dimension_code_expression=dimension_definition.code_expression,
                    dimension_name_expression=dimension_definition.name_expression,
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
                dimension_name=row.get("dimension_name"),
                negative_rate=float(row.get("negative_rate") or 0.0),
                active_hotspots=int(row.get("active_hotspots") or 0),
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
                dimension_name=row.get("dimension_name"),
                negative_rate=float(row.get("negative_rate") or 0.0),
                active_hotspots=int(row.get("active_hotspots") or 0),
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
        FROM {ANALYTICS_VIEW} AS item
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

    async def get_filter_options(
        self, filters: AnalyticsFilters
    ) -> dict[str, list[FilterOptionDTO]]:
        """Return data-backed options so UI labels always come from taxonomy."""
        where_clause, params = self._filter_query(filters)
        result = await self._session.execute(
            text(FILTER_OPTIONS_SQL.format(where_clause=where_clause)), params
        )
        options: dict[str, list[FilterOptionDTO]] = {
            "source_systems": [],
            "intake_channels": [],
            "affected_channels": [],
            "locations": [],
            "journey_stages": [],
            "journey_steps": [],
            "service_request_steps": [],
            "services": [],
            "issues": [],
        }
        for row in result.mappings().all():
            target = "source_systems" if row["option_type"] == "source_system" else "locations"
            options[target].append(
                FilterOptionDTO(
                    code=str(row["code"]),
                    name=str(row["name"]),
                    id=row.get("id"),
                )
            )

        taxonomy_result = await self._session.execute(
            text(TAXONOMY_FILTER_OPTIONS_SQL),
            {
                "taxonomy_stage_code": filters.customer_lifecycle_stage_code,
                "taxonomy_service_code": filters.service_code,
            },
        )
        taxonomy_option_targets = {
            "intake_channel": "intake_channels",
            "affected_channel": "affected_channels",
            "journey_stage": "journey_stages",
            "journey_step": "journey_steps",
            "service_request_step": "service_request_steps",
            "service": "services",
            "issue": "issues",
        }
        for row in taxonomy_result.mappings().all():
            options[taxonomy_option_targets[row["option_type"]]].append(
                FilterOptionDTO(
                    code=str(row["code"]),
                    name=str(row["name"]),
                    id=row.get("id"),
                )
            )
        options["sentiments"] = [
            FilterOptionDTO("POSITIVE", "Tích cực"),
            FilterOptionDTO("NEUTRAL", "Trung tính"),
            FilterOptionDTO("NEGATIVE", "Tiêu cực"),
            FilterOptionDTO("UNKNOWN", "Chưa xác định"),
        ]
        options["severities"] = [
            FilterOptionDTO("SEV-1", "Nghiêm trọng"),
            FilterOptionDTO("SEV-2", "Cao"),
            FilterOptionDTO("SEV-3", "Trung bình"),
            FilterOptionDTO("SEV-4", "Thấp"),
        ]
        return options

    @staticmethod
    def _filter_query(filters: AnalyticsFilters) -> tuple[str, dict[str, Any]]:
        """Compile only semantic-view backed filters into bound SQL parameters."""
        clauses = ["item.project_id = :project_id"]
        params: dict[str, Any] = {"project_id": filters.project_id}

        if filters.date_from is not None:
            clauses.append("item.reported_at >= :date_from")
            params["date_from"] = filters.date_from
        if filters.date_to is not None:
            clauses.append("item.reported_at < (:date_to + INTERVAL '1 day')")
            params["date_to"] = filters.date_to
        if filters.affected_channel_code is not None:
            clauses.append(":affected_channel_code = ANY(item.affected_channel_codes)")
            params["affected_channel_code"] = filters.affected_channel_code
        if filters.location_scope is not None:
            clauses.append("""
            item.location_id IN (
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
                clauses.append(f"item.{column_name} = :{field_name}")
                params[field_name] = str(value)
        return " AND ".join(clauses), params
