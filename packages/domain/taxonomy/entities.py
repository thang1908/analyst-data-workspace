"""Taxonomy domain entities including Touchpoints and Service Mappings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from packages.domain.shared.enums import MappingType


@dataclass(frozen=True, slots=True)
class CustomerLifecycleStage:
    customer_lifecycle_stage_id: UUID
    taxonomy_release_id: UUID
    stage_code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0
    active: bool = True


@dataclass(frozen=True, slots=True)
class CustomerLifecycleStep:
    customer_lifecycle_step_id: UUID
    taxonomy_release_id: UUID
    customer_lifecycle_stage_id: UUID
    step_code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0
    active: bool = True


@dataclass(frozen=True, slots=True)
class ServiceRequestStep:
    service_request_step_id: UUID
    taxonomy_release_id: UUID
    step_code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0
    active: bool = True


@dataclass(frozen=True, slots=True)
class Service:
    service_id: UUID
    taxonomy_release_id: UUID
    service_code: str
    name_vi: str
    name_en: str | None = None
    default_severity: str = "SEV-3"
    definition: str | None = None
    sort_order: int = 0
    active: bool = True


@dataclass(frozen=True, slots=True)
class Issue:
    issue_id: UUID
    taxonomy_release_id: UUID
    service_id: UUID
    issue_code: str
    name_vi: str
    name_en: str | None = None
    safety_critical: bool = False
    definition: str | None = None
    sort_order: int = 0
    active: bool = True


@dataclass(frozen=True, slots=True)
class Touchpoint:
    touchpoint_id: UUID
    taxonomy_release_id: UUID
    customer_lifecycle_step_id: UUID
    touchpoint_code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0
    active: bool = True
    active_from: datetime | None = None
    active_to: datetime | None = None


@dataclass(frozen=True, slots=True)
class TouchpointServiceMap:
    touchpoint_service_map_id: UUID
    taxonomy_release_id: UUID
    touchpoint_id: UUID
    service_id: UUID
    mapping_type: MappingType = MappingType.PRIMARY
    active: bool = True
