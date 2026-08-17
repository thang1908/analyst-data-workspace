"""Pydantic schemas for Taxonomy HTTP API."""
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BaseTaxonomyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReferenceItem(BaseTaxonomyModel):
    id: UUID | None = None
    code: str
    name_vi: str | None = None


class StageResponseItem(BaseTaxonomyModel):
    id: UUID
    code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0


class StepResponseItem(BaseTaxonomyModel):
    id: UUID
    code: str
    stage: ReferenceItem
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    sort_order: int = 0


class TouchpointServiceItem(BaseTaxonomyModel):
    id: UUID
    code: str
    name_vi: str
    mapping_type: str = "PRIMARY"


class TouchpointResponseItem(BaseTaxonomyModel):
    id: UUID
    code: str
    name_vi: str
    name_en: str | None = None
    definition: str | None = None
    lifecycle_step: ReferenceItem
    services: list[TouchpointServiceItem] = []
    sort_order: int = 0
    active: bool = True


class ServiceResponseItem(BaseTaxonomyModel):
    id: UUID
    code: str
    name_vi: str
    name_en: str | None = None
    default_severity: str = "SEV-3"
    definition: str | None = None
    sort_order: int = 0


class IssueResponseItem(BaseTaxonomyModel):
    id: UUID
    code: str
    service: ReferenceItem
    name_vi: str
    name_en: str | None = None
    safety_critical: bool = False
    definition: str | None = None
    sort_order: int = 0
