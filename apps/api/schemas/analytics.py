"""OpenAPI response models for P0 analytics endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base response model with stable JSON field names."""

    model_config = ConfigDict(extra="forbid")


class AnalyticsMeta(APIModel):
    """Metadata shared by dashboard analytics responses."""

    metric_definition_version: Literal["v1"] = "v1"
    filter_context: dict[str, str | None]


class SummaryData(APIModel):
    """Available summary metrics from the governed eligible-item view."""

    item_volume: int = Field(ge=0)
    csat_score: float = Field(ge=0, le=1)
    positive_rate: float = Field(ge=0, le=1)
    negative_rate: float = Field(ge=0, le=1)
    unknown_rate: float = Field(ge=0, le=1)
    active_hotspots: int = Field(ge=0)
    eligibility_definition_version: Literal["v1"] = "v1"


class SummaryResponse(APIModel):
    data: SummaryData
    meta: AnalyticsMeta


class TrendPoint(APIModel):
    bucket: datetime
    item_volume: int = Field(ge=0)
    negative_rate: float = Field(ge=0, le=1)
    unknown_rate: float = Field(ge=0, le=1)
    active_hotspots: int = Field(ge=0)


class TrendResponse(APIModel):
    data: list[TrendPoint]
    meta: AnalyticsMeta


class BreakdownDimension(APIModel):
    code: str
    name_vi: str


class BreakdownMetrics(APIModel):
    item_volume: int = Field(ge=0)
    percentage: float = Field(ge=0, le=1)
    negative_rate: float = Field(ge=0, le=1)
    active_hotspots: int = Field(ge=0)


class BreakdownItem(APIModel):
    dimension: BreakdownDimension
    metrics: BreakdownMetrics


class BreakdownResponse(APIModel):
    data: list[BreakdownItem]
    meta: AnalyticsMeta


class FilterOption(APIModel):
    code: str
    name_vi: str
    id: str | None = None


class AnalyticsFilterOptions(APIModel):
    source_systems: list[FilterOption]
    intake_channels: list[FilterOption]
    affected_channels: list[FilterOption]
    locations: list[FilterOption]
    journey_stages: list[FilterOption]
    journey_steps: list[FilterOption]
    service_request_steps: list[FilterOption]
    services: list[FilterOption]
    issues: list[FilterOption]
    sentiments: list[FilterOption]
    severities: list[FilterOption]


class FilterOptionsResponse(APIModel):
    data: AnalyticsFilterOptions
    meta: AnalyticsMeta


class DataQualityResponse(APIModel):
    """Reserved P0 response model; data quality metrics need a dedicated mart."""

    detail: str
