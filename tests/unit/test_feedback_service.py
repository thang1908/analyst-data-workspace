"""Application-service tests for Feedback aggregate persistence orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from packages.application.feedback import (
    CreateFeedbackCommand,
    FeedbackService,
    SplitFeedbackItemCommand,
)
from packages.domain.feedback import Feedback, FeedbackSplitResult, SplitItemDraft
from packages.domain.shared.exceptions import NotFoundError


@dataclass
class FakeFeedbackRepository:
    feedback: Feedback | None = None
    created: Feedback | None = None
    split_result: FeedbackSplitResult | None = None
    actor_role: str | None = None
    correlation_id: str | None = None

    async def create_feedback(self, feedback: Feedback) -> Feedback:
        self.created = feedback
        self.feedback = feedback
        return feedback

    async def get_feedback(self, feedback_id: UUID) -> Feedback | None:
        if self.feedback and self.feedback.feedback_id == feedback_id:
            return self.feedback
        return None

    async def apply_split(
        self,
        result: FeedbackSplitResult,
        *,
        actor_role: str,
        correlation_id: str,
    ) -> None:
        self.split_result = result
        self.feedback = result.feedback
        self.actor_role = actor_role
        self.correlation_id = correlation_id


def _command() -> CreateFeedbackCommand:
    return CreateFeedbackCommand(
        project_id=uuid4(),
        source_system="resident-app",
        reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
        content_raw="Email lan@example.com; thang máy chậm.",
    )


@pytest.mark.asyncio
async def test_create_persists_one_default_masked_atomic_item() -> None:
    repository = FakeFeedbackRepository()
    feedback = await FeedbackService(repository).create(_command())

    assert repository.created == feedback
    assert len(feedback.items) == 1
    assert feedback.content_masked == "Email [EMAIL]; thang máy chậm."
    assert feedback.items[0].item_text_masked == feedback.content_masked


@pytest.mark.asyncio
async def test_split_loads_the_envelope_and_persists_lineage_and_audit_context() -> None:
    repository = FakeFeedbackRepository()
    service = FeedbackService(repository)
    feedback = await service.create(_command())
    actor_id = uuid4()

    result = await service.split_item(
        SplitFeedbackItemCommand(
            feedback_id=feedback.feedback_id,
            source_feedback_item_id=feedback.items[0].feedback_item_id,
            items=(SplitItemDraft("Email support unavailable."), SplitItemDraft("Elevator is slow.")),
            reason="Two independent observable failures.",
            actor_id=actor_id,
            actor_role="REVIEWER",
            correlation_id="corr-feedback-split",
        )
    )

    assert repository.split_result == result
    assert repository.actor_role == "REVIEWER"
    assert repository.correlation_id == "corr-feedback-split"
    assert len(repository.feedback.items) == 3  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_get_and_split_make_missing_feedback_explicit() -> None:
    service = FeedbackService(FakeFeedbackRepository())
    missing_id = uuid4()

    with pytest.raises(NotFoundError, match="Feedback"):
        await service.get(missing_id)
    with pytest.raises(NotFoundError, match="Feedback"):
        await service.split_item(
            SplitFeedbackItemCommand(
                feedback_id=missing_id,
                source_feedback_item_id=uuid4(),
                items=(SplitItemDraft("First"), SplitItemDraft("Second")),
                reason="Independent failures.",
                actor_id=uuid4(),
                actor_role="REVIEWER",
                correlation_id="corr-missing-feedback",
            )
        )
