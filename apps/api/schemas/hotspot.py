"""Pydantic schemas for Hotspot HTTP API endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseHotspotModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HotspotRef(BaseHotspotModel):
    id: UUID | None = None
    code: str | None = None
    name_vi: str | None = None


class HotspotEvidenceSchema(BaseHotspotModel):
    feedback_item_id: UUID
    reported_at: datetime
    content_masked: str
    sentiment: str
    operational_severity: str
    evidence_role: str = "PRIMARY"


class HotspotTimelineSchema(BaseHotspotModel):
    timeline_event_id: UUID
    hotspot_id: UUID
    from_status: str | None = None
    to_status: str
    action: str
    actor_user_id: UUID
    reason: str | None = None
    metadata_json: dict[str, Any] | None = None
    correlation_id: str
    created_at: datetime


class HotspotItemData(BaseHotspotModel):
    hotspot_id: UUID
    project_id: UUID
    dimension_key: str
    service: HotspotRef
    issue: HotspotRef
    location: HotspotRef | None = None
    status: str
    action_priority: str
    operational_severity: str
    evidence_count: int
    assigned_user_id: UUID | None = None
    assigned_team_key: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime
    resolved_at: datetime | None = None
    resolution_summary: str | None = None
    window_start: datetime
    window_end: datetime
    version: int
    created_at: datetime
    updated_at: datetime


class HotspotListMeta(BaseHotspotModel):
    total: int
    limit: int
    offset: int


class HotspotListResponse(BaseHotspotModel):
    data: list[HotspotItemData]
    meta: HotspotListMeta


class HotspotDetailData(BaseHotspotModel):
    hotspot: HotspotItemData
    evidence: list[HotspotEvidenceSchema]
    timeline: list[HotspotTimelineSchema]


class HotspotDetailResponse(BaseHotspotModel):
    data: HotspotDetailData


# Mutation requests
class AcknowledgeHotspotRequest(BaseHotspotModel):
    expected_version: int | None = None
    reason: str | None = "Triage acknowledged by operations."


class AssignHotspotRequest(BaseHotspotModel):
    expected_version: int | None = None
    owner_user_id: UUID | None = None
    owner_team_key: str | None = None
    reason: str | None = "Assigned for investigation."


class DismissHotspotRequest(BaseHotspotModel):
    expected_version: int | None = None
    reason: str = Field(min_length=3, description="Reason for dismissing the hotspot is mandatory.")


class ResolveHotspotRequest(BaseHotspotModel):
    expected_version: int | None = None
    resolution_summary: str = Field(min_length=3, description="Operational resolution summary.")
    reason: str | None = "Hotspot resolved after operational fix."


class ReopenHotspotRequest(BaseHotspotModel):
    expected_version: int | None = None
    reason: str = Field(min_length=3, description="Reason for reopening the hotspot is mandatory.")


class DetectHotspotsRequest(BaseHotspotModel):
    project_id: UUID
    window_days: int = 180
    window_start: datetime | None = None
    window_end: datetime | None = None
    threshold_count: int = 3
    rule_version: str = "1.0.0"
    safety_playbook_approved: bool = False
