"""Masked Feedback Workspace endpoints."""
from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from apps.api.deps import get_feedback_repository
from apps.api.schemas.feedback import (
    CurrentClassification, FeedbackItemData, FeedbackItemDetailResponse,
    FeedbackItemListMeta, FeedbackItemListResponse, Location, Reference,
    SplitFeedbackItemRequest, SplitFeedbackItemResponse,
)
from packages.application.feedback import FeedbackService, SplitFeedbackItemCommand
from packages.domain.feedback import SplitItemDraft
from packages.domain.shared.exceptions import DomainError
from packages.infrastructure.db.repositories.feedback import (
    FeedbackItemListFilters, FeedbackItemWorkspaceRow, FeedbackRepository,
)

router = APIRouter(prefix="/api/v1/feedback-items", tags=["Feedback"])
FeedbackRepositoryDep = Annotated[FeedbackRepository, Depends(get_feedback_repository)]
ActorId = Annotated[UUID, Header(alias="X-Actor-ID")]
ActorRole = Annotated[str, Header(alias="X-Actor-Role")]
CorrelationId = Annotated[str | None, Header(alias="X-Correlation-ID")]


@router.get("", response_model=FeedbackItemListResponse, operation_id="listFeedbackItems")
async def list_feedback_items(
    repository: FeedbackRepositoryDep,
    project_id: UUID,
    date_from: date | None = None,
    date_to: date | None = None,
    source_system: str | None = None,
    intake_channel_code: str | None = None,
    affected_channel_code: str | None = None,
    location_id: UUID | None = None,
    service_code: str | None = None,
    issue_code: str | None = None,
    sentiment: str | None = None,
    operational_severity: str | None = None,
    customer_lifecycle_stage_code: str | None = None,
    customer_lifecycle_step_code: str | None = None,
    touchpoint_code: str | None = None,
    hotspot_id: UUID | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> FeedbackItemListResponse:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must not be later than date_to")
    rows, total = await repository.list_workspace_items(
        FeedbackItemListFilters(
            project_id=project_id,
            date_from=date_from,
            date_to=date_to,
            source_system=source_system,
            intake_channel_code=intake_channel_code,
            affected_channel_code=affected_channel_code,
            location_id=location_id,
            service_code=service_code,
            issue_code=issue_code,
            sentiment=sentiment,
            operational_severity=operational_severity,
            customer_lifecycle_stage_code=customer_lifecycle_stage_code,
            customer_lifecycle_step_code=customer_lifecycle_step_code,
            touchpoint_code=touchpoint_code,
            hotspot_id=hotspot_id,
            q=q,
            limit=limit,
            offset=offset,
        )
    )
    return FeedbackItemListResponse(
        data=[_item_data(row) for row in rows],
        meta=FeedbackItemListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{feedback_item_id}", response_model=FeedbackItemDetailResponse, operation_id="getFeedbackItem")
async def get_feedback_item(feedback_item_id: UUID, repository: FeedbackRepositoryDep) -> FeedbackItemDetailResponse:
    row = await repository.get_workspace_item(feedback_item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feedback item was not found.")
    return FeedbackItemDetailResponse(data=_item_data(row))


@router.post("/{feedback_item_id}/split", response_model=SplitFeedbackItemResponse, status_code=status.HTTP_201_CREATED, operation_id="splitFeedbackItem")
async def split_feedback_item(
    feedback_item_id: UUID, request: SplitFeedbackItemRequest, repository: FeedbackRepositoryDep,
    actor_id: ActorId, actor_role: ActorRole, correlation_id: CorrelationId = None,
) -> SplitFeedbackItemResponse:
    row = await repository.get_workspace_item(feedback_item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feedback item was not found.")
    try:
        result = await FeedbackService(repository).split_item(SplitFeedbackItemCommand(
            feedback_id=row.feedback_id, source_feedback_item_id=feedback_item_id,
            items=tuple(SplitItemDraft(item.item_text_masked, item.symptom_detail, item.location_id, tuple(item.affected_channel_ids)) for item in request.items),
            reason=request.reason, actor_id=actor_id, actor_role=actor_role,
            correlation_id=correlation_id or str(uuid4()),
        ))
    except DomainError as error:
        raise HTTPException(status_code=422, detail=error.message) from error
    return SplitFeedbackItemResponse(data={
        "source_item": {"id": str(result.source_item.feedback_item_id), "status": result.source_item.status},
        "created_items": [{"id": str(item.feedback_item_id), "item_index": item.item_index} for item in result.created_items],
    })


def _item_data(row: FeedbackItemWorkspaceRow) -> FeedbackItemData:
    return FeedbackItemData(
        feedback_item_id=row.feedback_item_id, feedback_id=row.feedback_id, reported_at=row.reported_at,
        source_system=row.source_system, content_masked=row.content_masked,
        location=Location(id=row.location_id, code=row.location_code, name=row.location_name),
        affected_channel_codes=list(row.affected_channel_codes), status=row.status,
        analytic_eligibility=row.analytic_eligibility, parent_item_id=row.parent_item_id,
        current_classification=CurrentClassification(
            service=Reference(code=row.service_code, name_vi=row.service_name_vi) if row.service_code else None,
            issue=Reference(code=row.issue_code, name_vi=row.issue_name_vi) if row.issue_code else None,
            sentiment=row.sentiment, operational_severity=row.operational_severity,
            classification_state=row.classification_state, projection_version=row.projection_version,
        ),
    )
