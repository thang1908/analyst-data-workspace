from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class TaxonomyServiceDTO(BaseModel):
    id: UUID
    code: str
    name: str
    active: bool = True


class TaxonomyIssueDTO(BaseModel):
    id: UUID
    code: str
    name: str
    active: bool = True


class LocationNodeDTO(BaseModel):
    id: UUID
    code: str
    name: str
    node_type: str
    parent_id: UUID | None = None


class ReferenceReleaseDTO(BaseModel):
    id: UUID
    kind: str  # TAXONOMY | LOCATION | SOURCE_TRUST
    version: str
    checksum_sha256: str
    published_at: datetime
