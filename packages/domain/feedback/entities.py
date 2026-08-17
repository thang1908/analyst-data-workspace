"""Pure domain entities for immutable feedback and atomic feedback items.

The aggregate intentionally keeps raw content only on :class:`Feedback`.
Derived items can carry only masked text, so downstream AI, review and
analytics code cannot accidentally use the privileged source envelope.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID, uuid4

from packages.domain.feedback.exceptions import FeedbackDomainError
from packages.domain.feedback.masking import mask_pii
from packages.domain.shared.enums import AnalyticEligibility, FeedbackItemStatus


class SplitSource(StrEnum):
    """The actor class that initiated an item split."""

    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"


def _required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise FeedbackDomainError(f"{field_name} must not be blank.")
    return normalized


def _aware_timestamp(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise FeedbackDomainError(f"{field_name} must be timezone-aware.")
    return value


@dataclass(frozen=True, slots=True)
class FeedbackItem:
    """One atomic, masked unit for classification, analytics and hotspots."""

    feedback_id: UUID
    item_index: int
    item_text_masked: str
    feedback_item_id: UUID = field(default_factory=uuid4)
    parent_item_id: UUID | None = None
    symptom_detail: str | None = None
    location_id: UUID | None = None
    affected_channel_ids: tuple[UUID, ...] = ()
    status: FeedbackItemStatus = FeedbackItemStatus.ACTIVE
    analytic_eligibility: AnalyticEligibility = AnalyticEligibility.PENDING
    eligibility_reason: str | None = None
    split_source: SplitSource | None = None
    split_by: UUID | None = None
    split_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: UUID | None = None

    def __post_init__(self) -> None:
        if self.item_index < 1:
            raise FeedbackDomainError("item_index must be at least 1.")
        object.__setattr__(self, "item_text_masked", _required_text(self.item_text_masked, "item_text_masked"))
        object.__setattr__(self, "affected_channel_ids", tuple(self.affected_channel_ids))
        _aware_timestamp(self.created_at, "created_at")

        split_metadata = (self.split_source, self.split_by, self.split_at)
        if any(value is not None for value in split_metadata) and not all(
            value is not None for value in split_metadata
        ):
            raise FeedbackDomainError(
                "split_source, split_by and split_at must be recorded together."
            )
        if self.split_at is not None:
            _aware_timestamp(self.split_at, "split_at")

    @property
    def is_active(self) -> bool:
        return self.status == FeedbackItemStatus.ACTIVE


@dataclass(frozen=True, slots=True)
class SplitItemDraft:
    """Masked data used to create one child item during an explicit split."""

    item_text_masked: str
    symptom_detail: str | None = None
    location_id: UUID | None = None
    affected_channel_ids: tuple[UUID, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "item_text_masked", _required_text(self.item_text_masked, "item_text_masked"))
        object.__setattr__(self, "affected_channel_ids", tuple(self.affected_channel_ids))


@dataclass(frozen=True, slots=True)
class FeedbackSplitEvent:
    """Immutable audit payload for persistence by the later application layer."""

    feedback_id: UUID
    source_feedback_item_id: UUID
    created_feedback_item_ids: tuple[UUID, ...]
    reason: str
    split_source: SplitSource
    actor_id: UUID
    occurred_at: datetime
    event_id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True, slots=True)
class FeedbackSplitResult:
    """The replacement aggregate and audit event produced by a split."""

    feedback: Feedback
    source_item: FeedbackItem
    created_items: tuple[FeedbackItem, ...]
    audit_event: FeedbackSplitEvent


@dataclass(frozen=True, slots=True)
class Feedback:
    """Immutable source envelope that owns one or more atomic feedback items."""

    project_id: UUID
    source_system: str
    reported_at: datetime
    content_raw: str
    content_masked: str
    items: tuple[FeedbackItem, ...]
    feedback_id: UUID = field(default_factory=uuid4)
    source_record_key: str | None = None
    intake_channel_id: UUID | None = None
    source_url: str | None = None
    external_ticket_id: str | None = None
    source_metadata: Mapping[str, Any] = field(default_factory=dict)
    raw_content_checksum: str | None = None
    ingested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_system", _required_text(self.source_system, "source_system"))
        object.__setattr__(self, "content_raw", _required_text(self.content_raw, "content_raw"))
        object.__setattr__(self, "content_masked", _required_text(self.content_masked, "content_masked"))
        _aware_timestamp(self.reported_at, "reported_at")
        _aware_timestamp(self.ingested_at, "ingested_at")
        _aware_timestamp(self.created_at, "created_at")

        items = tuple(self.items)
        if not items:
            raise FeedbackDomainError("Feedback must contain at least one FeedbackItem.")
        if any(item.feedback_id != self.feedback_id for item in items):
            raise FeedbackDomainError("Every FeedbackItem must belong to its Feedback envelope.")
        indexes = tuple(item.item_index for item in items)
        if len(set(indexes)) != len(indexes):
            raise FeedbackDomainError("FeedbackItem indexes must be unique within a Feedback envelope.")
        object.__setattr__(self, "items", tuple(sorted(items, key=lambda item: item.item_index)))
        object.__setattr__(self, "source_metadata", MappingProxyType(dict(self.source_metadata)))

        checksum = self.raw_content_checksum or sha256(self.content_raw.encode()).hexdigest()
        object.__setattr__(self, "raw_content_checksum", checksum)

    @classmethod
    def create(
        cls,
        *,
        project_id: UUID,
        source_system: str,
        reported_at: datetime,
        content_raw: str,
        content_masked: str | None = None,
        feedback_id: UUID | None = None,
        **envelope_fields: Any,
    ) -> Feedback:
        """Create the P0 default of one atomic item without exposing raw text."""
        identity = feedback_id or uuid4()
        masked_content = content_masked if content_masked is not None else mask_pii(content_raw)
        item = FeedbackItem(
            feedback_id=identity,
            item_index=1,
            item_text_masked=masked_content,
        )
        return cls(
            project_id=project_id,
            source_system=source_system,
            reported_at=reported_at,
            content_raw=content_raw,
            content_masked=masked_content,
            items=(item,),
            feedback_id=identity,
            **envelope_fields,
        )

    def get_item(self, feedback_item_id: UUID) -> FeedbackItem:
        """Return an item owned by this envelope, never by a global lookup."""
        for item in self.items:
            if item.feedback_item_id == feedback_item_id:
                return item
        raise FeedbackDomainError("FeedbackItem does not belong to this Feedback envelope.")

    def split_item(
        self,
        *,
        source_feedback_item_id: UUID,
        items: tuple[SplitItemDraft, ...],
        reason: str,
        actor_id: UUID,
        split_source: SplitSource = SplitSource.HUMAN,
        occurred_at: datetime | None = None,
    ) -> FeedbackSplitResult:
        """Split one active item while preserving the original raw envelope.

        The original aggregate is never mutated.  The returned replacement
        marks the source as ``SPLIT_PARENT`` and creates new child identities
        with fresh, stable indexes.
        """
        normalized_reason = _required_text(reason, "reason")
        if len(items) < 2:
            raise FeedbackDomainError("A split must create at least two atomic FeedbackItems.")
        timestamp = occurred_at or datetime.now(timezone.utc)
        _aware_timestamp(timestamp, "occurred_at")
        source_item = self.get_item(source_feedback_item_id)
        if not source_item.is_active:
            raise FeedbackDomainError("Only an ACTIVE FeedbackItem can be split.")

        next_index = max(item.item_index for item in self.items) + 1
        created_items = tuple(
            FeedbackItem(
                feedback_id=self.feedback_id,
                item_index=next_index + offset,
                item_text_masked=draft.item_text_masked,
                parent_item_id=source_item.feedback_item_id,
                symptom_detail=draft.symptom_detail,
                location_id=draft.location_id,
                affected_channel_ids=draft.affected_channel_ids,
                split_source=split_source,
                split_by=actor_id,
                split_at=timestamp,
                created_at=timestamp,
                created_by=actor_id,
            )
            for offset, draft in enumerate(items)
        )
        split_parent = replace(
            source_item,
            status=FeedbackItemStatus.SPLIT_PARENT,
            analytic_eligibility=AnalyticEligibility.EXCLUDED,
            eligibility_reason="SPLIT_PARENT",
        )
        replacement_items = tuple(
            split_parent if item.feedback_item_id == source_item.feedback_item_id else item
            for item in self.items
        ) + created_items
        replacement = replace(self, items=replacement_items)
        event = FeedbackSplitEvent(
            feedback_id=self.feedback_id,
            source_feedback_item_id=source_item.feedback_item_id,
            created_feedback_item_ids=tuple(item.feedback_item_id for item in created_items),
            reason=normalized_reason,
            split_source=split_source,
            actor_id=actor_id,
            occurred_at=timestamp,
        )
        return FeedbackSplitResult(
            feedback=replacement,
            source_item=split_parent,
            created_items=created_items,
            audit_event=event,
        )
