"""Hotspot domain entities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from packages.domain.shared.enums import ActionPriority, HotspotStatus, OperationalSeverity


@dataclass(frozen=True, slots=True)
class Hotspot:
    hotspot_id: UUID
    hotspot_rule_id: UUID
    project_id: UUID
    taxonomy_release_id: UUID
    dimension_key: str
    service_id: UUID
    issue_id: UUID
    window_start: datetime
    window_end: datetime
    evidence_count: int
    operational_severity: OperationalSeverity
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    location_id: UUID | None = None
    status: HotspotStatus = HotspotStatus.CANDIDATE
    action_priority: ActionPriority = ActionPriority.MONITOR
    assigned_user_id: UUID | None = None
    assigned_team_key: str | None = None
    resolved_at: datetime | None = None
    resolution_summary: str | None = None
    version: int = 1
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class FeedbackItemHotspot:
    hotspot_id: UUID
    feedback_item_id: UUID
    linked_at: datetime
    evidence_role: str = "PRIMARY"


@dataclass(frozen=True, slots=True)
class HotspotTimelineEvent:
    hotspot_timeline_event_id: UUID
    hotspot_id: UUID
    to_status: str
    action: str
    actor_user_id: UUID
    correlation_id: str
    created_at: datetime
    from_status: str | None = None
    reason: str | None = None
    metadata_json: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class HotspotRule:
    hotspot_rule_id: UUID
    name: str
    rule_version: str
    taxonomy_release_id: UUID
    window_minutes: int
    threshold_count: int
    location_level: str
    dimension_config_json: dict[str, Any]
    created_by: UUID
    created_at: datetime
    project_id: UUID | None = None
    eligibility_definition_version: str = "v1"
    active: bool = True
