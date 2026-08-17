"""Hotspot and Action Priority Queue HTTP API endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from apps.api.deps import get_hotspot_repository
from apps.api.schemas.hotspot import (
    AcknowledgeHotspotRequest,
    AssignHotspotRequest,
    DetectHotspotsRequest,
    DismissHotspotRequest,
    HotspotDetailData,
    HotspotDetailResponse,
    HotspotEvidenceSchema,
    HotspotItemData,
    HotspotListMeta,
    HotspotListResponse,
    HotspotRef,
    HotspotTimelineSchema,
    ReopenHotspotRequest,
    ResolveHotspotRequest,
)
from packages.domain.hotspot.exceptions import (
    ConcurrencyConflictError,
    HotspotDomainError,
    HotspotNotFoundError,
    InvalidStateTransitionError,
)
from packages.domain.shared.enums import HotspotStatus
from packages.infrastructure.db.repositories.hotspot import (
    HotspotDetail,
    HotspotListFilters,
    HotspotListItem,
    HotspotRepository,
)

router = APIRouter(prefix="/api/v1/hotspots", tags=["Hotspots"])
HotspotRepositoryDep = Annotated[HotspotRepository, Depends(get_hotspot_repository)]

ActorIdHeader = Annotated[UUID | None, Header(alias="X-Actor-ID")]
CorrelationIdHeader = Annotated[str | None, Header(alias="X-Correlation-ID")]

DEFAULT_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000001")


def _to_item_data(item: HotspotListItem) -> HotspotItemData:
    return HotspotItemData(
        hotspot_id=item.hotspot_id,
        project_id=item.project_id,
        dimension_key=item.dimension_key,
        service=HotspotRef(id=item.service_id, code=item.service_code, name_vi=item.service_name_vi),
        issue=HotspotRef(id=item.issue_id, code=item.issue_code, name_vi=item.issue_name_vi),
        location=HotspotRef(id=item.location_id, code=item.location_code, name_vi=item.location_name)
        if item.location_id or item.location_code
        else None,
        status=item.status,
        action_priority=item.action_priority,
        operational_severity=item.operational_severity,
        evidence_count=item.evidence_count,
        assigned_user_id=item.assigned_user_id,
        assigned_team_key=item.assigned_team_key,
        first_seen_at=item.first_seen_at,
        last_seen_at=item.last_seen_at,
        resolved_at=item.resolved_at,
        resolution_summary=item.resolution_summary,
        window_start=item.window_start,
        window_end=item.window_end,
        version=item.version,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_detail_response(detail: HotspotDetail) -> HotspotDetailResponse:
    return HotspotDetailResponse(
        data=HotspotDetailData(
            hotspot=_to_item_data(detail.hotspot),
            evidence=[
                HotspotEvidenceSchema(
                    feedback_item_id=e.feedback_item_id,
                    reported_at=e.reported_at,
                    content_masked=e.content_masked,
                    sentiment=e.sentiment,
                    operational_severity=e.operational_severity,
                    evidence_role=e.evidence_role,
                )
                for e in detail.evidence
            ],
            timeline=[
                HotspotTimelineSchema(
                    timeline_event_id=t.timeline_event_id,
                    hotspot_id=t.hotspot_id,
                    from_status=t.from_status,
                    to_status=t.to_status,
                    action=t.action,
                    actor_user_id=t.actor_user_id,
                    reason=t.reason,
                    metadata_json=t.metadata_json,
                    correlation_id=t.correlation_id,
                    created_at=t.created_at,
                )
                for t in detail.timeline
            ],
        )
    )


@router.get("", response_model=HotspotListResponse, operation_id="listHotspots")
async def list_hotspots(
    repository: HotspotRepositoryDep,
    project_id: UUID,
    status_filter: str | None = Query(None, alias="status"),
    action_priority: str | None = None,
    service_code: str | None = None,
    issue_code: str | None = None,
    location_id: UUID | None = None,
    severity: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> HotspotListResponse:
    items, total = await repository.list_hotspots(
        HotspotListFilters(
            project_id=project_id,
            status=status_filter,
            action_priority=action_priority,
            service_code=service_code,
            issue_code=issue_code,
            location_id=location_id,
            operational_severity=severity,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )
    return HotspotListResponse(
        data=[_to_item_data(item) for item in items],
        meta=HotspotListMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{hotspot_id}", response_model=HotspotDetailResponse, operation_id="getHotspot")
async def get_hotspot(
    hotspot_id: UUID,
    repository: HotspotRepositoryDep,
) -> HotspotDetailResponse:
    detail = await repository.get_hotspot(hotspot_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotspot was not found.")
    return _to_detail_response(detail)


@router.post("/{hotspot_id}/acknowledge", response_model=HotspotDetailResponse, operation_id="acknowledgeHotspot")
async def acknowledge_hotspot(
    hotspot_id: UUID,
    request: AcknowledgeHotspotRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
    correlation_id: CorrelationIdHeader = None,
) -> HotspotDetailResponse:
    try:
        detail = await repository.mutate_hotspot_status(
            hotspot_id,
            action="ACKNOWLEDGE",
            to_status=HotspotStatus.ACKNOWLEDGED.value,
            actor_user_id=actor_id or DEFAULT_ACTOR_ID,
            reason=request.reason,
            expected_version=request.expected_version,
            correlation_id=correlation_id,
        )
        return _to_detail_response(detail)
    except ConcurrencyConflictError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err)) from err
    except InvalidStateTransitionError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from err
    except HotspotNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err


@router.post("/{hotspot_id}/assign", response_model=HotspotDetailResponse, operation_id="assignHotspot")
async def assign_hotspot(
    hotspot_id: UUID,
    request: AssignHotspotRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
    correlation_id: CorrelationIdHeader = None,
) -> HotspotDetailResponse:
    try:
        detail = await repository.mutate_hotspot_status(
            hotspot_id,
            action="ASSIGN",
            to_status=HotspotStatus.INVESTIGATING.value,
            actor_user_id=actor_id or DEFAULT_ACTOR_ID,
            assigned_user_id=request.owner_user_id,
            assigned_team_key=request.owner_team_key,
            reason=request.reason,
            expected_version=request.expected_version,
            correlation_id=correlation_id,
        )
        return _to_detail_response(detail)
    except ConcurrencyConflictError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err)) from err
    except InvalidStateTransitionError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from err
    except HotspotNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err


@router.post("/{hotspot_id}/dismiss", response_model=HotspotDetailResponse, operation_id="dismissHotspot")
async def dismiss_hotspot(
    hotspot_id: UUID,
    request: DismissHotspotRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
    correlation_id: CorrelationIdHeader = None,
) -> HotspotDetailResponse:
    try:
        detail = await repository.mutate_hotspot_status(
            hotspot_id,
            action="DISMISS",
            to_status=HotspotStatus.DISMISSED.value,
            actor_user_id=actor_id or DEFAULT_ACTOR_ID,
            reason=request.reason,
            expected_version=request.expected_version,
            correlation_id=correlation_id,
        )
        return _to_detail_response(detail)
    except ConcurrencyConflictError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err)) from err
    except InvalidStateTransitionError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from err
    except HotspotNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err


@router.post("/{hotspot_id}/resolve", response_model=HotspotDetailResponse, operation_id="resolveHotspot")
async def resolve_hotspot(
    hotspot_id: UUID,
    request: ResolveHotspotRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
    correlation_id: CorrelationIdHeader = None,
) -> HotspotDetailResponse:
    try:
        detail = await repository.mutate_hotspot_status(
            hotspot_id,
            action="RESOLVE",
            to_status=HotspotStatus.RESOLVED.value,
            actor_user_id=actor_id or DEFAULT_ACTOR_ID,
            reason=request.reason,
            resolution_summary=request.resolution_summary,
            expected_version=request.expected_version,
            correlation_id=correlation_id,
        )
        return _to_detail_response(detail)
    except ConcurrencyConflictError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err)) from err
    except InvalidStateTransitionError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from err
    except HotspotNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err


@router.post("/{hotspot_id}/reopen", response_model=HotspotDetailResponse, operation_id="reopenHotspot")
async def reopen_hotspot(
    hotspot_id: UUID,
    request: ReopenHotspotRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
    correlation_id: CorrelationIdHeader = None,
) -> HotspotDetailResponse:
    try:
        detail = await repository.mutate_hotspot_status(
            hotspot_id,
            action="REOPEN",
            to_status=HotspotStatus.INVESTIGATING.value,
            actor_user_id=actor_id or DEFAULT_ACTOR_ID,
            reason=request.reason,
            expected_version=request.expected_version,
            correlation_id=correlation_id,
        )
        return _to_detail_response(detail)
    except ConcurrencyConflictError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err)) from err
    except InvalidStateTransitionError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from err
    except HotspotNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err


@router.post("/detect", response_model=HotspotListResponse, operation_id="detectHotspots")
async def detect_hotspots(
    request: DetectHotspotsRequest,
    repository: HotspotRepositoryDep,
    actor_id: ActorIdHeader = None,
) -> HotspotListResponse:
    now = datetime.now(timezone.utc)
    w_end = request.window_end or now
    w_start = request.window_start or (
        datetime.fromtimestamp(w_end.timestamp() - request.window_days * 86400, tz=timezone.utc)
    )

    items = await repository.detect_and_sync_hotspots(
        project_id=request.project_id,
        window_start=w_start,
        window_end=w_end,
        threshold_count=request.threshold_count,
        rule_version=request.rule_version,
        actor_user_id=actor_id or DEFAULT_ACTOR_ID,
        safety_playbook_approved=request.safety_playbook_approved,
    )
    return HotspotListResponse(
        data=[_to_item_data(item) for item in items],
        meta=HotspotListMeta(total=len(items), limit=len(items), offset=0),
    )
