"""Application use cases for creating, retrieving and splitting feedback."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Protocol
from uuid import UUID

from packages.domain.feedback import (
    Feedback,
    FeedbackSplitResult,
    SplitItemDraft,
    SplitSource,
)
from packages.domain.shared.exceptions import NotFoundError


@dataclass(frozen=True, slots=True)
class CreateFeedbackCommand:
    """The trusted ingestion payload for one immutable feedback envelope."""

    project_id: UUID
    source_system: str
    reported_at: datetime
    content_raw: str
    content_masked: str | None = None
    source_record_key: str | None = None
    intake_channel_id: UUID | None = None
    source_url: str | None = None
    external_ticket_id: str | None = None
    source_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SplitFeedbackItemCommand:
    """An explicit multi-intent split requested by a reviewer or system actor."""

    feedback_id: UUID
    source_feedback_item_id: UUID
    items: tuple[SplitItemDraft, ...]
    reason: str
    actor_id: UUID
    actor_role: str
    correlation_id: str
    split_source: SplitSource = SplitSource.HUMAN
    occurred_at: datetime | None = None


class FeedbackRepository(Protocol):
    """Persistence port for the Feedback aggregate."""

    async def create_feedback(self, feedback: Feedback) -> Feedback:
        """Persist an immutable envelope and all of its initial items."""
        ...

    async def get_feedback(self, feedback_id: UUID) -> Feedback | None:
        """Rehydrate one feedback aggregate including its atomic items."""
        ...

    async def apply_split(
        self,
        result: FeedbackSplitResult,
        *,
        actor_role: str,
        correlation_id: str,
    ) -> None:
        """Persist a split parent, child items and mandatory audit event atomically."""
        ...


class FeedbackService:
    """Coordinate the Feedback aggregate without exposing persistence details."""

    def __init__(self, repository: FeedbackRepository) -> None:
        self._repository = repository

    async def create(self, command: CreateFeedbackCommand) -> Feedback:
        """Store an immutable envelope with the P0 default atomic item."""
        feedback = Feedback.create(
            project_id=command.project_id,
            source_system=command.source_system,
            reported_at=command.reported_at,
            content_raw=command.content_raw,
            content_masked=command.content_masked,
            source_record_key=command.source_record_key,
            intake_channel_id=command.intake_channel_id,
            source_url=command.source_url,
            external_ticket_id=command.external_ticket_id,
            source_metadata=command.source_metadata,
        )
        return await self._repository.create_feedback(feedback)

    async def get(self, feedback_id: UUID) -> Feedback:
        """Load the complete aggregate or make the missing resource explicit."""
        feedback = await self._repository.get_feedback(feedback_id)
        if feedback is None:
            raise NotFoundError("Feedback", feedback_id)
        return feedback

    async def split_item(self, command: SplitFeedbackItemCommand) -> FeedbackSplitResult:
        """Apply a provenance-preserving split and persist its audit event."""
        feedback = await self.get(command.feedback_id)
        result = feedback.split_item(
            source_feedback_item_id=command.source_feedback_item_id,
            items=command.items,
            reason=command.reason,
            actor_id=command.actor_id,
            split_source=command.split_source,
            occurred_at=command.occurred_at,
        )
        await self._repository.apply_split(
            result,
            actor_role=command.actor_role,
            correlation_id=command.correlation_id,
        )
        return result
