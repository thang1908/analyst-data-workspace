"""SQL-shape tests for Feedback repository writes."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from packages.domain.feedback import Feedback, SplitItemDraft
from packages.infrastructure.db.repositories.feedback import FeedbackRepository


def _session(*, update_succeeds: bool = True) -> AsyncMock:
    update_result = MagicMock()
    update_result.scalar_one_or_none.return_value = uuid4() if update_succeeds else None
    session = AsyncMock()
    session.execute = AsyncMock(return_value=update_result)
    return session


def _feedback() -> Feedback:
    return Feedback.create(
        project_id=uuid4(),
        source_system="resident-app",
        reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
        content_raw="Email lan@example.com; thang máy chậm.",
    )


@pytest.mark.asyncio
async def test_create_writes_the_envelope_then_its_atomic_item() -> None:
    session = _session()
    feedback = _feedback()

    await FeedbackRepository(session).create_feedback(feedback)

    statements = [call.args[0].text for call in session.execute.await_args_list]
    assert "INSERT INTO feedback" in statements[0]
    assert "content_raw" in statements[0]
    assert "content_masked" in statements[0]
    assert "INSERT INTO feedback_item" in statements[1]
    assert "item_text_masked" in statements[1]


@pytest.mark.asyncio
async def test_split_persists_parent_children_and_a_non_pii_audit_event() -> None:
    session = _session()
    feedback = _feedback()
    result = feedback.split_item(
        source_feedback_item_id=feedback.items[0].feedback_item_id,
        items=(SplitItemDraft("Email support unavailable."), SplitItemDraft("Elevator is slow.")),
        reason="Two independent observable failures.",
        actor_id=uuid4(),
    )

    await FeedbackRepository(session).apply_split(
        result,
        actor_role="REVIEWER",
        correlation_id="corr-feedback-split",
    )

    statements = [call.args[0].text for call in session.execute.await_args_list]
    assert "UPDATE feedback_item" in statements[0]
    assert "status = 'ACTIVE'" in statements[0]
    assert sum("INSERT INTO feedback_item" in statement for statement in statements) == 2
    audit_statement = next(statement for statement in statements if "INSERT INTO audit_event" in statement)
    assert "feedback_item.split" in audit_statement
    assert "content_raw" not in audit_statement
