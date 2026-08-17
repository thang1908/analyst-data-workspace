"""PostgreSQL integration coverage for Feedback aggregate persistence.

Run explicitly with:
    RUN_FEEDBACK_INTEGRATION_TESTS=1 uv run pytest tests/integration/test_feedback_repository.py
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.feedback import Feedback, SplitItemDraft
from packages.infrastructure.db.repositories.feedback import FeedbackItemListFilters, FeedbackRepository
from packages.infrastructure.db.session import engine

if os.getenv("RUN_FEEDBACK_INTEGRATION_TESTS") != "1":
    pytestmark = pytest.mark.skip(
        reason="set RUN_FEEDBACK_INTEGRATION_TESTS=1 to use local PostgreSQL"
    )


@pytest.mark.asyncio
async def test_feedback_repository_persists_envelope_items_and_split_audit() -> None:
    actor_id = uuid4()
    feedback = Feedback.create(
        project_id=uuid4(),
        source_system=f"feedback-integration-{uuid4()}",
        source_record_key="source-1",
        reported_at=datetime(2026, 8, 17, 9, tzinfo=timezone.utc),
        content_raw="Liên hệ lan@example.com hoặc 0901234567: thang máy chậm và app lỗi.",
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            repository = FeedbackRepository(session)
            assert await repository.create_feedback(feedback) == feedback

            loaded = await repository.get_feedback(feedback.feedback_id)
            assert loaded is not None
            assert loaded.content_raw == feedback.content_raw
            assert loaded.content_masked == "Liên hệ [EMAIL] hoặc [PHONE]: thang máy chậm và app lỗi."
            assert len(loaded.items) == 1

            workspace_rows, total = await repository.list_workspace_items(
                FeedbackItemListFilters(
                    project_id=feedback.project_id,
                    source_system=feedback.source_system,
                )
            )
            assert total == 1
            assert workspace_rows[0].feedback_item_id == loaded.items[0].feedback_item_id
            assert workspace_rows[0].content_masked == loaded.content_masked
            assert "0901234567" not in workspace_rows[0].content_masked
            assert await repository.get_workspace_item(loaded.items[0].feedback_item_id) is not None

            split = loaded.split_item(
                source_feedback_item_id=loaded.items[0].feedback_item_id,
                items=(SplitItemDraft("Thang máy chậm."), SplitItemDraft("App cư dân lỗi.")),
                reason="Two independent observable failures.",
                actor_id=actor_id,
            )
            await repository.apply_split(
                split,
                actor_role="REVIEWER",
                correlation_id="feedback-repository-integration",
            )

            rows = (await session.execute(
                text("""
                    SELECT item_index, status, parent_item_id
                    FROM feedback_item
                    WHERE feedback_id = :feedback_id
                    ORDER BY item_index
                """),
                {"feedback_id": feedback.feedback_id},
            )).mappings().all()
            assert [(row["item_index"], row["status"]) for row in rows] == [
                (1, "SPLIT_PARENT"), (2, "ACTIVE"), (3, "ACTIVE")
            ]
            assert all(row["parent_item_id"] == loaded.items[0].feedback_item_id for row in rows[1:])
            audit = (await session.execute(
                text("""
                    SELECT action, reason, metadata_json
                    FROM audit_event
                    WHERE audit_event_id = :audit_event_id
                """),
                {"audit_event_id": split.audit_event.event_id},
            )).mappings().one()
            assert audit["action"] == "feedback_item.split"
            assert audit["reason"] == "Two independent observable failures."
            assert str(feedback.feedback_id) in audit["metadata_json"].values()
        finally:
            await session.close()
            await transaction.rollback()
