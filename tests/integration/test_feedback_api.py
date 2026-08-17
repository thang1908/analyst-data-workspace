"""HTTP contracts for masked Feedback Workspace endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from apps.api.deps import get_feedback_repository
from apps.api.main import app
from packages.domain.feedback import Feedback, FeedbackSplitResult
from packages.infrastructure.db.repositories.feedback import (
    FeedbackItemListFilters,
    FeedbackItemWorkspaceRow,
)


class StubFeedbackRepository:
    def __init__(self) -> None:
        self.feedback = Feedback.create(
            project_id=uuid4(), source_system="resident-app",
            reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
            content_raw="Raw phone 0901234567 must never be sent.",
        )
        item = self.feedback.items[0]
        self.row = FeedbackItemWorkspaceRow(
            feedback_item_id=item.feedback_item_id, feedback_id=self.feedback.feedback_id,
            reported_at=self.feedback.reported_at, source_system="resident-app",
            content_masked="Raw phone [PHONE] must never be sent.", location_id=None,
            location_code=None, location_name=None, service_code=None, service_name_vi=None,
            issue_code=None, issue_name_vi=None, sentiment=None, operational_severity=None,
            classification_state="PENDING_REVIEW", projection_version=None, status="ACTIVE",
            analytic_eligibility="PENDING", parent_item_id=None, affected_channel_codes=("CH-APP",),
        )
        self.filters: FeedbackItemListFilters | None = None
        self.split: FeedbackSplitResult | None = None

    async def list_workspace_items(self, filters: FeedbackItemListFilters) -> tuple[list[FeedbackItemWorkspaceRow], int]:
        self.filters = filters
        return [self.row], 1

    async def get_workspace_item(self, feedback_item_id: UUID) -> FeedbackItemWorkspaceRow | None:
        return self.row if feedback_item_id == self.row.feedback_item_id else None

    async def get_feedback(self, feedback_id: UUID) -> Feedback | None:
        return self.feedback if feedback_id == self.feedback.feedback_id else None

    async def create_feedback(self, feedback: Feedback) -> Feedback:
        return feedback

    async def apply_split(self, result: FeedbackSplitResult, *, actor_role: str, correlation_id: str) -> None:
        del actor_role, correlation_id
        self.split = result
        self.feedback = result.feedback


def _client() -> tuple[TestClient, StubFeedbackRepository]:
    repository = StubFeedbackRepository()
    app.dependency_overrides[get_feedback_repository] = lambda: repository
    return TestClient(app), repository


def test_list_filters_and_never_exposes_raw_content() -> None:
    client, repository = _client()
    try:
        response = client.get(
            "/api/v1/feedback-items",
            params={
                "project_id": repository.feedback.project_id,
                "date_from": "2026-08-01", "date_to": "2026-08-31",
                "intake_channel_code": "CH-APP", "affected_channel_code": "CH-HOTLINE",
                "limit": 20, "offset": 0,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert repository.filters is not None
    assert repository.filters.affected_channel_code == "CH-HOTLINE"
    body = response.json()
    assert body["meta"] == {"total": 1, "limit": 20, "offset": 0}
    assert body["data"][0]["content_masked"] == "Raw phone [PHONE] must never be sent."
    assert "content_raw" not in str(body)
    assert "0901234567" not in str(body)


def test_detail_and_split_contracts() -> None:
    client, repository = _client()
    try:
        detail = client.get(f"/api/v1/feedback-items/{repository.row.feedback_item_id}")
        split = client.post(
            f"/api/v1/feedback-items/{repository.row.feedback_item_id}/split",
            headers={"X-Actor-ID": str(uuid4()), "X-Actor-Role": "REVIEWER"},
            json={
                "reason": "Two independent observable failures.",
                "items": [
                    {"item_text_masked": "First failure."},
                    {"item_text_masked": "Second failure."},
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert detail.status_code == 200
    assert detail.json()["data"]["affected_channel_codes"] == ["CH-APP"]
    assert split.status_code == 201
    assert repository.split is not None
    assert split.json()["data"]["source_item"]["status"] == "SPLIT_PARENT"
    assert [item["item_index"] for item in split.json()["data"]["created_items"]] == [2, 3]
