from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    """Base domain model configuration."""

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class EntityId(DomainModel):
    """Strongly typed base for entity identifiers."""

    value: UUID = Field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)


class TimestampedDomainModel(DomainModel):
    """Base model containing standard timestamp attributes."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
