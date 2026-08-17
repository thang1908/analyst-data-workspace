"""Unit tests for the immutable feedback envelope and atomic split behavior."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from packages.domain.feedback import (
    Feedback,
    FeedbackDomainError,
    SplitItemDraft,
    SplitSource,
)
from packages.domain.shared.enums import AnalyticEligibility, FeedbackItemStatus


def _feedback() -> Feedback:
    return Feedback.create(
        project_id=uuid4(),
        source_system="resident-app",
        reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
        content_raw="Chị Lan, 0901234567: thang máy chậm và app cư dân không đăng nhập được.",
        content_masked="[Người dùng], [SĐT]: thang máy chậm và app cư dân không đăng nhập được.",
    )


def test_feedback_create_is_an_immutable_envelope_with_one_default_item() -> None:
    feedback = _feedback()

    assert len(feedback.items) == 1
    assert feedback.items[0].item_index == 1
    assert feedback.items[0].item_text_masked == feedback.content_masked
    assert len(feedback.raw_content_checksum) == 64
    with pytest.raises(FrozenInstanceError):
        feedback.content_raw = "rewritten"  # type: ignore[misc]
    with pytest.raises(TypeError):
        feedback.source_metadata["pii"] = "must not mutate"  # type: ignore[index]


def test_feedback_create_masks_pii_when_a_display_safe_value_is_not_supplied() -> None:
    feedback = Feedback.create(
        project_id=uuid4(),
        source_system="resident-app",
        reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
        content_raw="Liên hệ lan.nguyen@example.com hoặc 0901234567.",
    )

    assert feedback.content_raw == "Liên hệ lan.nguyen@example.com hoặc 0901234567."
    assert feedback.content_masked == "Liên hệ [EMAIL] hoặc [PHONE]."
    assert feedback.items[0].item_text_masked == feedback.content_masked


def test_feedback_requires_at_least_one_item_owned_by_its_envelope() -> None:
    feedback = _feedback()

    with pytest.raises(FeedbackDomainError, match="at least one"):
        Feedback(
            project_id=feedback.project_id,
            source_system=feedback.source_system,
            reported_at=feedback.reported_at,
            content_raw=feedback.content_raw,
            content_masked=feedback.content_masked,
            items=(),
        )


def test_split_creates_atomic_masked_children_and_preserves_raw_provenance() -> None:
    feedback = _feedback()
    source = feedback.items[0]
    actor_id = uuid4()
    split_at = datetime(2026, 8, 17, 10, tzinfo=timezone.utc)

    result = feedback.split_item(
        source_feedback_item_id=source.feedback_item_id,
        reason="Two independent observable failures.",
        actor_id=actor_id,
        occurred_at=split_at,
        items=(
            SplitItemDraft("Thang máy chậm vào buổi sáng.", symptom_detail="Chờ thang máy lâu"),
            SplitItemDraft("App cư dân không đăng nhập được.", symptom_detail="Lỗi OTP/login"),
        ),
    )

    assert feedback.content_raw == "Chị Lan, 0901234567: thang máy chậm và app cư dân không đăng nhập được."
    assert feedback.items[0].status == FeedbackItemStatus.ACTIVE
    assert len(result.feedback.items) == 3
    assert result.source_item.status == FeedbackItemStatus.SPLIT_PARENT
    assert result.source_item.analytic_eligibility == AnalyticEligibility.EXCLUDED
    assert [item.item_index for item in result.created_items] == [2, 3]
    assert all(item.feedback_id == feedback.feedback_id for item in result.created_items)
    assert all(item.parent_item_id == source.feedback_item_id for item in result.created_items)
    assert all(item.split_source == SplitSource.HUMAN for item in result.created_items)
    assert all(item.split_by == actor_id and item.split_at == split_at for item in result.created_items)
    assert result.audit_event.reason == "Two independent observable failures."
    assert result.audit_event.created_feedback_item_ids == tuple(item.feedback_item_id for item in result.created_items)


@pytest.mark.parametrize(
    ("items", "reason", "message"),
    [
        ((SplitItemDraft("Only one child"),), "valid reason", "at least two"),
        (
            (SplitItemDraft("First child"), SplitItemDraft("Second child")),
            " ",
            "reason must not be blank",
        ),
    ],
)
def test_split_rejects_non_atomic_or_unjustified_requests(
    items: tuple[SplitItemDraft, ...], reason: str, message: str
) -> None:
    feedback = _feedback()

    with pytest.raises(FeedbackDomainError, match=message):
        feedback.split_item(
            source_feedback_item_id=feedback.items[0].feedback_item_id,
            items=items,
            reason=reason,
            actor_id=uuid4(),
        )


def test_split_rejects_parent_or_item_not_owned_by_the_envelope() -> None:
    feedback = _feedback()
    result = feedback.split_item(
        source_feedback_item_id=feedback.items[0].feedback_item_id,
        items=(SplitItemDraft("One failure"), SplitItemDraft("Another failure")),
        reason="Independent failures.",
        actor_id=uuid4(),
    )

    with pytest.raises(FeedbackDomainError, match="Only an ACTIVE"):
        result.feedback.split_item(
            source_feedback_item_id=result.source_item.feedback_item_id,
            items=(SplitItemDraft("Again one"), SplitItemDraft("Again two")),
            reason="Try to split parent.",
            actor_id=uuid4(),
        )
    with pytest.raises(FeedbackDomainError, match="does not belong"):
        feedback.get_item(uuid4())
