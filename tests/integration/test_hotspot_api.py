"""HTTP contract tests for Hotspot API endpoints and state mutations."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from apps.api.deps import get_hotspot_repository
from apps.api.main import app
from packages.infrastructure.db.repositories.hotspot import (
    HotspotDetail,
    HotspotEvidenceItem,
    HotspotListFilters,
    HotspotListItem,
    HotspotTimelineItem,
)


class StubHotspotRepository:
    def __init__(self) -> None:
        self.hotspot_id = uuid4()
        self.project_id = uuid4()
        self.service_id = uuid4()
        self.issue_id = uuid4()
        self.now = datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)
        self.status = "CANDIDATE"
        self.version = 1
        self.action_priority = "URGENT"

    def _sample_item(self) -> HotspotListItem:
        return HotspotListItem(
            hotspot_id=self.hotspot_id,
            project_id=self.project_id,
            dimension_key="SV-05:IS-05-01:LOC-01:1.0.0",
            service_id=self.service_id,
            service_code="SV-05",
            service_name_vi="Ra vào & bãi xe",
            issue_id=self.issue_id,
            issue_code="IS-05-01",
            issue_name_vi="Ra vào hoặc tiếp khách",
            location_id=uuid4(),
            location_code="LOC-01",
            location_name="Tòa Landmark",
            status=self.status,
            action_priority=self.action_priority,
            operational_severity="SEV-2",
            evidence_count=5,
            assigned_user_id=None,
            assigned_team_key=None,
            first_seen_at=self.now,
            last_seen_at=self.now,
            resolved_at=None,
            resolution_summary=None,
            window_start=self.now,
            window_end=self.now,
            version=self.version,
            created_at=self.now,
            updated_at=self.now,
        )

    async def list_hotspots(self, filters: HotspotListFilters) -> tuple[list[HotspotListItem], int]:
        return [self._sample_item()], 1

    async def get_hotspot(self, hotspot_id: UUID) -> HotspotDetail | None:
        if hotspot_id != self.hotspot_id:
            return None
        return HotspotDetail(
            hotspot=self._sample_item(),
            evidence=[
                HotspotEvidenceItem(
                    feedback_item_id=uuid4(),
                    reported_at=self.now,
                    content_masked="Thẻ cư dân quẹt không mở cổng",
                    sentiment="NEGATIVE",
                    operational_severity="SEV-2",
                    evidence_role="PRIMARY",
                )
            ],
            timeline=[
                HotspotTimelineItem(
                    timeline_event_id=uuid4(),
                    hotspot_id=self.hotspot_id,
                    from_status=None,
                    to_status="CANDIDATE",
                    action="DETECTED",
                    actor_user_id=uuid4(),
                    reason="Deterministic cluster matched threshold",
                    metadata_json={"count": 5},
                    correlation_id=str(uuid4()),
                    created_at=self.now,
                )
            ],
        )

    async def mutate_hotspot_status(
        self,
        hotspot_id: UUID,
        *,
        action: str,
        to_status: str,
        actor_user_id: UUID,
        reason: str | None = None,
        resolution_summary: str | None = None,
        assigned_user_id: UUID | None = None,
        assigned_team_key: str | None = None,
        expected_version: int | None = None,
        correlation_id: str | None = None,
    ) -> HotspotDetail:
        self.status = to_status
        self.version += 1
        res = await self.get_hotspot(hotspot_id)
        assert res is not None
        return res

    async def detect_and_sync_hotspots(
        self,
        project_id: UUID,
        *,
        window_start: datetime,
        window_end: datetime,
        threshold_count: int = 3,
        rule_version: str = "1.0.0",
        actor_user_id: UUID | None = None,
        safety_playbook_approved: bool = False,
    ) -> list[HotspotListItem]:
        return [self._sample_item()]


def _client() -> tuple[TestClient, StubHotspotRepository]:
    stub = StubHotspotRepository()

    async def override_repository() -> StubHotspotRepository:
        return stub

    app.dependency_overrides[get_hotspot_repository] = override_repository
    return TestClient(app), stub


def test_list_hotspots_endpoint() -> None:
    client, stub = _client()
    try:
        res = client.get(f"/api/v1/hotspots?project_id={stub.project_id}")
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()
    assert data["meta"]["total"] == 1
    assert data["data"][0]["hotspot_id"] == str(stub.hotspot_id)
    assert data["data"][0]["action_priority"] == "URGENT"
    assert data["data"][0]["service"]["code"] == "SV-05"


def test_get_hotspot_detail_endpoint() -> None:
    client, stub = _client()
    try:
        res = client.get(f"/api/v1/hotspots/{stub.hotspot_id}")
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()["data"]
    assert data["hotspot"]["hotspot_id"] == str(stub.hotspot_id)
    assert len(data["evidence"]) == 1
    assert len(data["timeline"]) == 1
    assert data["timeline"][0]["action"] == "DETECTED"


def test_acknowledge_and_assign_and_resolve_mutations() -> None:
    client, stub = _client()
    try:
        # Acknowledge
        res_ack = client.post(
            f"/api/v1/hotspots/{stub.hotspot_id}/acknowledge",
            json={"expected_version": 1, "reason": "Triage accepted"},
        )
        assert res_ack.status_code == 200
        assert res_ack.json()["data"]["hotspot"]["status"] == "ACKNOWLEDGED"

        # Assign
        assign_user = uuid4()
        res_assign = client.post(
            f"/api/v1/hotspots/{stub.hotspot_id}/assign",
            json={"expected_version": 2, "owner_user_id": str(assign_user), "reason": "Assigned to tech lead"},
        )
        assert res_assign.status_code == 200
        assert res_assign.json()["data"]["hotspot"]["status"] == "INVESTIGATING"

        # Resolve
        res_res = client.post(
            f"/api/v1/hotspots/{stub.hotspot_id}/resolve",
            json={"expected_version": 3, "resolution_summary": "Access card firmware patch applied"},
        )
        assert res_res.status_code == 200
        assert res_res.json()["data"]["hotspot"]["status"] == "RESOLVED"

        # Reopen from resolved
        res_reopen = client.post(
            f"/api/v1/hotspots/{stub.hotspot_id}/reopen",
            json={"expected_version": 4, "reason": "Issue resurfaced in tower B"},
        )
        assert res_reopen.status_code == 200
        assert res_reopen.json()["data"]["hotspot"]["status"] == "INVESTIGATING"

        # Dismiss
        res_dismiss = client.post(
            f"/api/v1/hotspots/{stub.hotspot_id}/dismiss",
            json={"expected_version": 5, "reason": "External power outage false alarm"},
        )
        assert res_dismiss.status_code == 200
        assert res_dismiss.json()["data"]["hotspot"]["status"] == "DISMISSED"
    finally:
        app.dependency_overrides.clear()


def test_hotspot_not_found_returns_404() -> None:
    client, _ = _client()
    non_existent = uuid4()
    try:
        res = client.get(f"/api/v1/hotspots/{non_existent}")
        assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_detect_hotspots_endpoint() -> None:
    client, stub = _client()
    try:
        res = client.post(
            "/api/v1/hotspots/detect",
            json={"project_id": str(stub.project_id), "window_days": 30, "threshold_count": 3},
        )
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    assert len(res.json()["data"]) == 1


def test_list_hotspots_invalid_date_range_returns_422() -> None:
    client, stub = _client()
    try:
        res = client.get(
            f"/api/v1/hotspots?project_id={stub.project_id}&date_from=2026-08-20&date_to=2026-08-10"
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides.clear()

