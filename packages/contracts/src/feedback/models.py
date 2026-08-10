from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ProvenanceDTO(BaseModel):
    import_job_id: UUID
    source_reference: str
    row_index: int
    decision: str = "SOURCE_TRUSTED"
    committed_at: datetime


class FeedbackItemSummaryDTO(BaseModel):
    feedback_item_id: UUID
    created_at: datetime
    service_name: str
    issue_name: Optional[str] = None
    location_name: Optional[str] = None
    sentiment: str
    severity: str
    masked_text: str


class FeedbackItemDetailDTO(BaseModel):
    feedback_item_id: UUID
    created_at: datetime
    service_name: str
    issue_name: Optional[str] = None
    location_name: Optional[str] = None
    sentiment: str
    severity: str
    masked_text: str
    provenance: ProvenanceDTO


class FeedbackItemListResponse(BaseModel):
    items: list[FeedbackItemSummaryDTO]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_matching: int = 0
