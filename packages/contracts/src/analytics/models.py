from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AnalyticsFilterParams(BaseModel):
    from_date: date = Field(..., description="Start date (inclusive)")
    to_date: date = Field(..., description="End date (inclusive)")
    project_code: Optional[list[str]] = Field(None, description="Project codes filter")
    building_code: Optional[list[str]] = Field(None, description="Building codes filter")
    location_code: Optional[list[str]] = Field(None, description="Location codes filter")
    service_code: Optional[list[str]] = Field(None, description="Service codes filter")
    issue_code: Optional[list[str]] = Field(None, description="Issue codes filter")
    sentiment: Optional[list[str]] = Field(None, description="Sentiment filter")
    operational_severity: Optional[list[str]] = Field(None, description="Severity filter")
    customer_lifecycle_stages: Optional[list[str]] = Field(None, description="ADR-001 Dim A Stage filter")
    service_request_steps: Optional[list[str]] = Field(None, description="ADR-001 Dim B Step filter")
    snapshot_token: Optional[str] = Field(None, description="Opaque snapshot token for consistency")


class AnalyticsSummaryDTO(BaseModel):
    snapshot_token: str
    snapshot_at: datetime
    timezone: str = "Asia/Ho_Chi_Minh"
    item_volume: int = Field(..., description="Total eligible feedback items count")
    negative_feedback_count: int = Field(..., description="Negative feedback items count")
    negative_rate: Optional[float] = Field(..., description="Ratio of negative / known sentiment items")
    sentiment_known_count: int = Field(..., description="Items with known sentiment count")
    high_severity_count: int = Field(..., description="High severity (SEV-1/SEV-2) items count")


class DailyTrendPointDTO(BaseModel):
    date: date
    total_count: int
    negative_count: int
    negative_rate: Optional[float]


class AnalyticsTrendDTO(BaseModel):
    snapshot_token: str
    snapshot_at: datetime
    timezone: str = "Asia/Ho_Chi_Minh"
    points: list[DailyTrendPointDTO]


class BreakdownSegmentDTO(BaseModel):
    key: str
    label: str
    total_count: int
    share: float
    negative_count: int


class AnalyticsBreakdownDTO(BaseModel):
    dimension: str
    snapshot_token: str
    snapshot_at: datetime
    segments: list[BreakdownSegmentDTO]
    other_count: int = 0


class AnalyticsContextDTO(BaseModel):
    projects: list[dict[str, str]]
    services: list[dict[str, str]]
    locations: list[dict[str, str]]
    snapshot_token: str
    snapshot_at: datetime


class DataQualitySummaryDTO(BaseModel):
    snapshot_token: str
    snapshot_at: datetime
    total_jobs: int
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    pass_rate: float
