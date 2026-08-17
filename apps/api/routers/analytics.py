"""P0 analytics HTTP endpoints backed by the governed semantic view."""
from __future__ import annotations

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.api.deps import get_analytics_repository
from apps.api.schemas.analytics import (
    AnalyticsMeta,
    BreakdownDimension,
    BreakdownItem,
    BreakdownMetrics,
    BreakdownResponse,
    DataQualityResponse,
    AnalyticsFilterOptions,
    SummaryData,
    SummaryResponse,
    TrendPoint,
    TrendResponse,
    FilterOption,
    FilterOptionsResponse,
)
from packages.application.analytics.analytics_service import AnalyticsFilters
from packages.domain.shared.enums import OperationalSeverity, Sentiment
from packages.infrastructure.db.repositories.analytics import AnalyticsRepository

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

AnalyticsRepositoryDep = Annotated[AnalyticsRepository, Depends(get_analytics_repository)]
AnalyticsGrain = Literal["day", "week", "month"]
AnalyticsDimension = Literal[
    "service",
    "issue",
    "location",
    "journey_stage",
    "journey_step",
    "touchpoint",
    "service_request_step",
    "intake_channel",
    "affected_channel",
    "sentiment",
    "severity",
]


def shared_filters(
    project_id: UUID,
    date_from: date | None = None,
    date_to: date | None = None,
    source_system: str | None = None,
    intake_channel_code: str | None = None,
    affected_channel_code: str | None = None,
    location_id: UUID | None = None,
    location_scope: UUID | None = None,
    customer_lifecycle_stage_code: str | None = None,
    customer_lifecycle_step_code: str | None = None,
    touchpoint_code: str | None = None,
    service_request_step_code: str | None = None,
    service_code: str | None = None,
    issue_code: str | None = None,
    sentiment: Sentiment | None = None,
    operational_severity: OperationalSeverity | None = None,
) -> AnalyticsFilters:
    """Parse the one shared P0 dashboard filter context for every route."""
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from must not be later than date_to",
        )
    return AnalyticsFilters(
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        source_system=source_system,
        intake_channel_code=intake_channel_code,
        affected_channel_code=affected_channel_code,
        location_id=location_id,
        location_scope=location_scope,
        customer_lifecycle_stage_code=customer_lifecycle_stage_code,
        customer_lifecycle_step_code=customer_lifecycle_step_code,
        touchpoint_code=touchpoint_code,
        service_request_step_code=service_request_step_code,
        service_code=service_code,
        issue_code=issue_code,
        sentiment=sentiment,
        operational_severity=operational_severity,
    )


AnalyticsFiltersDep = Annotated[AnalyticsFilters, Depends(shared_filters)]


def _meta(filters: AnalyticsFilters) -> AnalyticsMeta:
    """Return JSON-safe filter metadata for a future drill-down consumer."""
    return AnalyticsMeta(
        filter_context={
            name: str(value) if value is not None else None
            for name, value in (
                ("project_id", filters.project_id),
                ("date_from", filters.date_from),
                ("date_to", filters.date_to),
                ("source_system", filters.source_system),
                ("intake_channel_code", filters.intake_channel_code),
                ("affected_channel_code", filters.affected_channel_code),
                ("location_id", filters.location_id),
                ("location_scope", filters.location_scope),
                ("customer_lifecycle_stage_code", filters.customer_lifecycle_stage_code),
                ("customer_lifecycle_step_code", filters.customer_lifecycle_step_code),
                ("touchpoint_code", filters.touchpoint_code),
                ("service_request_step_code", filters.service_request_step_code),
                ("service_code", filters.service_code),
                ("issue_code", filters.issue_code),
                ("sentiment", filters.sentiment),
                ("operational_severity", filters.operational_severity),
            )
        },
    )


@router.get(
    "/summary",
    response_model=SummaryResponse,
    operation_id="getAnalyticsSummary",
)
async def get_summary(
    filters: AnalyticsFiltersDep,
    repository: AnalyticsRepositoryDep,
) -> SummaryResponse:
    """Return eligible feedback-item volume and sentiment-derived rates."""
    summary = await repository.get_summary(filters)
    return SummaryResponse(
        data=SummaryData(
            item_volume=summary.total,
            csat_score=summary.csat_score,
            positive_rate=summary.positive_rate,
            negative_rate=summary.negative_rate,
            unknown_rate=summary.unknown_rate,
            active_hotspots=summary.active_hotspots,
        ),
        meta=_meta(filters),
    )


@router.get("/trend", response_model=TrendResponse, operation_id="getAnalyticsTrend")
async def get_trend(
    filters: AnalyticsFiltersDep,
    repository: AnalyticsRepositoryDep,
    grain: AnalyticsGrain = Query("day"),
    metric: Literal["item_volume", "negative_rate", "unknown_rate", "active_hotspots"] = Query("item_volume"),
) -> TrendResponse:
    """Return P0 item-volume trend by day, week, or month."""
    del metric  # All P0 trend metrics are returned from the same governed bucket series.
    trend = await repository.get_trend(filters, grain)
    return TrendResponse(
        data=[
            TrendPoint(
                bucket=point.time_bucket,
                item_volume=point.volume,
                negative_rate=point.negative_rate,
                unknown_rate=point.unknown_rate,
                active_hotspots=point.active_hotspots,
            )
            for point in trend
        ],
        meta=_meta(filters),
    )


@router.get(
    "/breakdown",
    response_model=BreakdownResponse,
    operation_id="getAnalyticsBreakdown",
)
async def get_breakdown(
    filters: AnalyticsFiltersDep,
    repository: AnalyticsRepositoryDep,
    dimension: AnalyticsDimension,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> BreakdownResponse:
    """Return a dimension breakdown from the same shared filter context."""
    breakdown = await repository.get_breakdown(filters, dimension)
    return BreakdownResponse(
        data=[
            BreakdownItem(
                dimension=BreakdownDimension(
                    code=item.dimension_key,
                    name_vi=item.dimension_name or item.dimension_key,
                ),
                metrics=BreakdownMetrics(
                    item_volume=item.count,
                    percentage=item.percentage,
                    negative_rate=item.negative_rate,
                    active_hotspots=item.active_hotspots,
                ),
            )
            for item in breakdown[:limit]
        ],
        meta=_meta(filters),
    )


@router.get(
    "/filter-options",
    response_model=FilterOptionsResponse,
    operation_id="getAnalyticsFilterOptions",
)
async def get_filter_options(
    filters: AnalyticsFiltersDep,
    repository: AnalyticsRepositoryDep,
) -> FilterOptionsResponse:
    """Return human-readable, data-backed values for the shared P0 filters."""
    options = await repository.get_filter_options(filters)
    return FilterOptionsResponse(
        data=AnalyticsFilterOptions(
            **{
                field: [FilterOption(code=item.code, name_vi=item.name, id=item.id) for item in values]
                for field, values in options.items()
            }
        ),
        meta=_meta(filters),
    )


@router.get(
    "/data-quality",
    response_model=DataQualityResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    operation_id="getAnalyticsDataQuality",
)
async def get_data_quality(filters: AnalyticsFiltersDep) -> DataQualityResponse:
    """Reserve the route until a separate non-eligible data quality mart exists."""
    del filters
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "data-quality requires a dedicated quality mart because the governed "
            "analytics view contains eligible items only"
        ),
    )
