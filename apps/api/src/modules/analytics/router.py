from datetime import date, datetime
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Query

from cx_contracts.analytics.models import (
    AnalyticsBreakdownDTO,
    AnalyticsContextDTO,
    AnalyticsSummaryDTO,
    AnalyticsTrendDTO,
    BreakdownSegmentDTO,
    DailyTrendPointDTO,
    DataQualitySummaryDTO,
)

analytics_router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@analytics_router.get("/context", response_model=AnalyticsContextDTO)
async def get_analytics_context() -> AnalyticsContextDTO:
    now = datetime.utcnow()
    return AnalyticsContextDTO(
        projects=[{"code": "PROJ_PILOT", "name": "Pilot CX Project"}],
        services=[
            {"code": "SRV_SUPPORT", "name": "Customer Support"},
            {"code": "SRV_BILLING", "name": "Billing Services"},
            {"code": "SRV_PRODUCT", "name": "Product Features"},
        ],
        locations=[
            {"code": "LOC_BLDG_A", "name": "Building A"},
            {"code": "LOC_BLDG_B", "name": "Building B"},
        ],
        snapshot_token=f"snap_{now.strftime('%Y%m%d_%H%M%S')}",
        snapshot_at=now,
    )


@analytics_router.get("/summary", response_model=AnalyticsSummaryDTO)
async def get_analytics_summary(
    from_date: date = Query(...),
    to_date: date = Query(...),
    project_code: Optional[list[str]] = Query(None),
    service_code: Optional[list[str]] = Query(None),
    snapshot_token: Optional[str] = Query(None),
) -> AnalyticsSummaryDTO:
    now = datetime.utcnow()
    token = snapshot_token or f"snap_{now.strftime('%Y%m%d_%H%M%S')}"
    return AnalyticsSummaryDTO(
        snapshot_token=token,
        snapshot_at=now,
        timezone="Asia/Ho_Chi_Minh",
        item_volume=9850,
        negative_feedback_count=1398,
        negative_rate=0.1419,
        sentiment_known_count=9850,
        high_severity_count=420,
    )


@analytics_router.get("/trend", response_model=AnalyticsTrendDTO)
async def get_analytics_trend(
    from_date: date = Query(...),
    to_date: date = Query(...),
    service_code: Optional[list[str]] = Query(None),
    snapshot_token: Optional[str] = Query(None),
) -> AnalyticsTrendDTO:
    now = datetime.utcnow()
    token = snapshot_token or f"snap_{now.strftime('%Y%m%d_%H%M%S')}"
    points = [
        DailyTrendPointDTO(date=date(2026, 8, 1), total_count=950, negative_count=120, negative_rate=0.1263),
        DailyTrendPointDTO(date=date(2026, 8, 2), total_count=1100, negative_count=180, negative_rate=0.1636),
        DailyTrendPointDTO(date=date(2026, 8, 3), total_count=1250, negative_count=190, negative_rate=0.1520),
        DailyTrendPointDTO(date=date(2026, 8, 4), total_count=1050, negative_count=140, negative_rate=0.1333),
        DailyTrendPointDTO(date=date(2026, 8, 5), total_count=1300, negative_count=210, negative_rate=0.1615),
        DailyTrendPointDTO(date=date(2026, 8, 6), total_count=1400, negative_count=195, negative_rate=0.1393),
        DailyTrendPointDTO(date=date(2026, 8, 7), total_count=1350, negative_count=185, negative_rate=0.1370),
    ]
    return AnalyticsTrendDTO(
        snapshot_token=token,
        snapshot_at=now,
        points=points,
    )


@analytics_router.get("/breakdowns/{dimension}", response_model=AnalyticsBreakdownDTO)
async def get_analytics_breakdown(
    dimension: str,
    from_date: date = Query(...),
    to_date: date = Query(...),
    snapshot_token: Optional[str] = Query(None),
) -> AnalyticsBreakdownDTO:
    now = datetime.utcnow()
    token = snapshot_token or f"snap_{now.strftime('%Y%m%d_%H%M%S')}"
    
    if dimension == "service":
        segments = [
            BreakdownSegmentDTO(key="SRV_SUPPORT", label="Customer Support", total_count=4812, share=0.4885, negative_count=820),
            BreakdownSegmentDTO(key="SRV_BILLING", label="Billing Services", total_count=3540, share=0.3594, negative_count=410),
            BreakdownSegmentDTO(key="SRV_PRODUCT", label="Product Features", total_count=1498, share=0.1521, negative_count=168),
        ]
    elif dimension == "location":
        segments = [
            BreakdownSegmentDTO(key="LOC_BLDG_A", label="Building A", total_count=5200, share=0.5279, negative_count=780),
            BreakdownSegmentDTO(key="LOC_BLDG_B", label="Building B", total_count=4650, share=0.4721, negative_count=618),
        ]
    else:
        segments = [
            BreakdownSegmentDTO(key="NEGATIVE", label="Negative", total_count=1398, share=0.1419, negative_count=1398),
            BreakdownSegmentDTO(key="POSITIVE", label="Positive", total_count=6450, share=0.6548, negative_count=0),
            BreakdownSegmentDTO(key="NEUTRAL", label="Neutral", total_count=2002, share=0.2033, negative_count=0),
        ]

    return AnalyticsBreakdownDTO(
        dimension=dimension,
        snapshot_token=token,
        snapshot_at=now,
        segments=segments,
        other_count=0,
    )


@analytics_router.get("/data-quality", response_model=DataQualitySummaryDTO)
async def get_data_quality_summary(
    from_date: date = Query(...),
    to_date: date = Query(...),
    snapshot_token: Optional[str] = Query(None),
) -> DataQualitySummaryDTO:
    now = datetime.utcnow()
    token = snapshot_token or f"snap_{now.strftime('%Y%m%d_%H%M%S')}"
    return DataQualitySummaryDTO(
        snapshot_token=token,
        snapshot_at=now,
        total_jobs=1,
        total_rows=10000,
        valid_rows=9850,
        invalid_rows=150,
        duplicate_rows=0,
        pass_rate=0.985,
    )
