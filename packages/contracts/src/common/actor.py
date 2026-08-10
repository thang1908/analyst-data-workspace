from uuid import UUID
from pydantic import BaseModel, Field


class ActorContext(BaseModel):
    actor_id: str = Field(..., description="ID of the authenticated actor or system principal")
    permissions: list[str] = Field(default_factory=list, description="Assigned permission scopes")
    project_ids: list[UUID] = Field(default_factory=list, description="Authorized project scopes")
    correlation_id: str = Field(..., description="Request correlation ID for tracing")
