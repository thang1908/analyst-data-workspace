"""HTTP contract tests for the P0 analytics API routes."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from apps.api.deps import get_analytics_repository
from apps.api.main import app
from packages.domain.analytics.dto import BreakdownItemDTO, FilterOptionDTO, SummaryDTO, TrendPointDTO


class StubAnalyticsRepository:
    async def get_summary(self, _filters: object) -> SummaryDTO:
        return SummaryDTO(
            total=4,
            csat_score=1 / 3,
            positive_rate=1 / 3,
            negative_rate=1 / 3,
            sentiment_unknown_rate=0.25,
        )

    async def get_trend(self, _filters: object, _grain: str) -> list[TrendPointDTO]:
        return [TrendPointDTO(datetime(2026, 8, 10, tzinfo=timezone.utc), 4)]

    async def get_breakdown(
        self, _filters: object, _dimension: str
    ) -> list[BreakdownItemDTO]:
        return [BreakdownItemDTO("SV-07", 4, 1.0)]

    async def get_filter_options(self, _filters: object) -> dict[str, list[FilterOptionDTO]]:
        empty = []
        return {
            "source_systems": empty,
            "intake_channels": [FilterOptionDTO("CH-APP", "Ứng dụng di động")],
            "affected_channels": empty,
            "locations": empty,
            "journey_stages": empty,
            "journey_steps": empty,
            "service_request_steps": empty,
            "services": [FilterOptionDTO("SV-07", "Kỹ thuật")],
            "issues": empty,
            "sentiments": empty,
            "severities": empty,
        }


def _client() -> TestClient:
    async def override_repository() -> StubAnalyticsRepository:
        return StubAnalyticsRepository()

    app.dependency_overrides[get_analytics_repository] = override_repository
    return TestClient(app)


def test_summary_returns_the_governed_response_envelope() -> None:
    client = _client()
    try:
        response = client.get(f"/api/v1/analytics/summary?project_id={uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"] == {
        "item_volume": 4,
        "csat_score": 1 / 3,
        "positive_rate": 1 / 3,
        "negative_rate": 1 / 3,
        "unknown_rate": 0.25,
        "active_hotspots": 0,
        "eligibility_definition_version": "v1",
    }
    assert response.json()["meta"]["filter_context"]["project_id"]


def test_trend_and_breakdown_share_filter_context_and_validate_params() -> None:
    client = _client()
    project_id = uuid4()
    try:
        trend_response = client.get(
            "/api/v1/analytics/trend",
            params={
                "project_id": project_id,
                "date_from": "2026-08-10",
                "date_to": "2026-08-11",
                "affected_channel_code": "CH-HOTLINE",
            },
        )
        breakdown_response = client.get(
            f"/api/v1/analytics/breakdown?project_id={project_id}&dimension=service"
        )
        invalid_response = client.get("/api/v1/analytics/summary")
        invalid_date_response = client.get(
            f"/api/v1/analytics/summary?project_id={project_id}"
            "&date_from=2026-08-12&date_to=2026-08-11"
        )
    finally:
        app.dependency_overrides.clear()

    assert trend_response.status_code == 200
    assert trend_response.json()["data"][0]["item_volume"] == 4
    assert trend_response.json()["meta"]["filter_context"]["affected_channel_code"] == "CH-HOTLINE"
    assert breakdown_response.status_code == 200
    assert breakdown_response.json()["data"][0]["dimension"]["code"] == "SV-07"
    assert breakdown_response.json()["data"][0]["dimension"]["name_vi"] == "SV-07"
    assert invalid_response.status_code == 422
    assert invalid_date_response.status_code == 422


def test_filter_options_return_human_readable_taxonomy_labels() -> None:
    client = _client()
    try:
        response = client.get(f"/api/v1/analytics/filter-options?project_id={uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["intake_channels"] == [
        {"code": "CH-APP", "name_vi": "Ứng dụng di động", "id": None}
    ]


def test_data_quality_route_is_explicitly_unavailable_until_its_mart_exists() -> None:
    response = TestClient(app).get(f"/api/v1/analytics/data-quality?project_id={uuid4()}")

    assert response.status_code == 501
    assert "dedicated quality mart" in response.json()["detail"]
