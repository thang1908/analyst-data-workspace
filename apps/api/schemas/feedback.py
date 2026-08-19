"""Public, masked-only HTTP contracts for Feedback Workspace APIs."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackAPIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Reference(FeedbackAPIModel):
    code: str | None = None
    name_vi: str | None = None


class Location(FeedbackAPIModel):
    id: UUID | None = None
    code: str | None = None
    name: str | None = None


class CurrentClassification(FeedbackAPIModel):
    service: Reference | None = None
    issue: Reference | None = None
    journey_stage: Reference | None = None
    journey_step: Reference | None = None
    touchpoint: Reference | None = None
    sentiment: str | None = None
    operational_severity: str | None = None
    classification_state: str | None = None
    projection_version: int | None = None


class FeedbackItemData(FeedbackAPIModel):
    feedback_item_id: UUID
    feedback_id: UUID
    reported_at: datetime
    source_system: str
    content_masked: str
    location: Location
    affected_channel_codes: list[str]
    current_classification: CurrentClassification
    status: str
    analytic_eligibility: str
    parent_item_id: UUID | None = None


class FeedbackItemListMeta(FeedbackAPIModel):
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class FeedbackItemListResponse(FeedbackAPIModel):
    data: list[FeedbackItemData]
    meta: FeedbackItemListMeta


class FeedbackItemDetailResponse(FeedbackAPIModel):
    data: FeedbackItemData


class SplitItemRequest(FeedbackAPIModel):
    item_text_masked: str = Field(min_length=1)
    symptom_detail: str | None = None
    location_id: UUID | None = None
    affected_channel_ids: list[UUID] = []


class SplitFeedbackItemRequest(FeedbackAPIModel):
    reason: str = Field(min_length=1)
    items: list[SplitItemRequest] = Field(min_length=2)


class SplitFeedbackItemResponse(FeedbackAPIModel):
    data: dict[str, object]


class UpdateFeedbackItemRequest(FeedbackAPIModel):
    service_code: str | None = None
    issue_code: str | None = None
    sentiment: str | None = None
    operational_severity: str | None = None
    analytic_eligibility: str | None = None
    location_id: UUID | None = None
    symptom_detail: str | None = None
    correction_reason: str | None = None
