"""Masked Feedback Workspace endpoints."""
from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import date, datetime, timezone
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile, status
from sqlalchemy import text

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


@router.post("/direct-import-csv")
async def direct_import_csv(
    repository: FeedbackRepositoryDep,
    file: UploadFile = File(...),
    project_id: UUID = UUID("00000000-0000-0000-0000-000000000001"),
) -> dict[str, Any]:
    """Directly and synchronously import a CSV file into Postgres without S3 or async worker."""
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=422, detail="Tệp CSV rỗng, vui lòng kiểm tra lại.")

    text_content = raw_bytes.decode("utf-8-sig", errors="ignore")
    raw_lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    if not raw_lines:
        raise HTTPException(status_code=422, detail="Tệp không có dòng dữ liệu nào.")

    # Check if lines were exported with outer double-quotes escaping
    first = raw_lines[0]
    if first.startswith('"') and first.endswith('"') and (',""' in first or '\t""' in first or '"",' in first):
        unquoted = []
        for l in raw_lines:
            if l.startswith('"') and l.endswith('"'):
                l = l[1:-1].replace('""', '"')
            unquoted.append(l)
        text_content = "\n".join(unquoted)

    first_line = text_content.split("\n", 1)[0]
    delimiter = "\t" if "\t" in first_line else ";" if (";" in first_line and "," not in first_line) else ","
    
    reader = csv.DictReader(io.StringIO(text_content), delimiter=delimiter)
    rows: list[dict[str, str]] = []
    for r in reader:
        cleaned = {k.strip().strip('"'): (v.strip().strip('"') if isinstance(v, str) else v) for k, v in r.items() if k is not None}
        rows.append(cleaned)

    if not rows:
        raise HTTPException(status_code=422, detail="Tệp không có dòng dữ liệu nào.")

    session = repository._session

    # Fetch taxonomy release
    tax_result = await session.execute(text("SELECT taxonomy_release_id FROM taxonomy_release WHERE status = 'PUBLISHED' LIMIT 1"))
    taxonomy_release_id = tax_result.scalar_one_or_none()
    if not taxonomy_release_id:
        tax_result = await session.execute(text("SELECT taxonomy_release_id FROM taxonomy_release LIMIT 1"))
        taxonomy_release_id = tax_result.scalar_one_or_none()
        if not taxonomy_release_id:
            taxonomy_release_id = UUID("00000000-0000-0000-0000-000000000010")

    default_proj_id = project_id or UUID("00000000-0000-0000-0000-000000000001")

    # Fetch services
    services_res = await session.execute(text("SELECT service_id, service_code, name_vi FROM service"))
    services = services_res.mappings().all()
    default_service_id = services[0]["service_id"] if services else None

    # Fetch issues
    issues_res = await session.execute(text("SELECT issue_id, issue_code, name_vi FROM issue"))
    issues = issues_res.mappings().all()
    default_issue_id = issues[0]["issue_id"] if issues else None

    # Fetch lifecycle steps & stages
    steps_res = await session.execute(text("SELECT customer_lifecycle_step_id, customer_lifecycle_stage_id, step_code, name_vi FROM customer_lifecycle_step"))
    all_steps = steps_res.mappings().all()
    
    stages_res = await session.execute(text("SELECT customer_lifecycle_stage_id, stage_code, name_vi FROM customer_lifecycle_stage"))
    all_stages = stages_res.mappings().all()

    default_step = next((s for s in all_steps if s["step_code"] in ["RES-07", "RES-01"]), all_steps[0] if all_steps else None)
    default_step_id = default_step["customer_lifecycle_step_id"] if default_step else None
    default_stage_id = default_step["customer_lifecycle_stage_id"] if default_step else None

    # Fetch locations
    locs_res = await session.execute(text("SELECT location_id, name, location_code FROM location"))
    locations = list(locs_res.mappings().all())

    now = datetime.now(timezone.utc)
    imported_count = 0

    feedback_batch: list[dict[str, Any]] = []
    item_batch: list[dict[str, Any]] = []
    decision_batch: list[dict[str, Any]] = []
    current_batch: list[dict[str, Any]] = []

    async def flush_batches() -> None:
        if feedback_batch:
            await session.execute(
                text("""
                    INSERT INTO feedback (
                        feedback_id, project_id, source_system, source_record_key, external_ticket_id,
                        reported_at, ingested_at, content_raw, content_masked,
                        source_metadata_json, raw_content_checksum, created_at
                    ) VALUES (
                        :feedback_id, :project_id, 'direct-csv', :source_record_key, :external_ticket_id,
                        :reported_at, :now, :content_raw, :content_masked,
                        '{}'::jsonb, :checksum, :now
                    )
                """),
                feedback_batch,
            )
            feedback_batch.clear()

        if item_batch:
            await session.execute(
                text("""
                    INSERT INTO feedback_item (
                        feedback_item_id, feedback_id, item_index, item_text_masked,
                        location_id, status, analytic_eligibility
                    ) VALUES (
                        :feedback_item_id, :feedback_id, 1, :masked_content,
                        :location_id, 'ACTIVE', 'INCLUDED'
                    )
                """),
                item_batch,
            )
            item_batch.clear()

        if decision_batch:
            await session.execute(
                text("""
                    INSERT INTO classification_decision (
                        classification_decision_id, feedback_item_id, decision_version, taxonomy_release_id,
                        customer_lifecycle_value_status, customer_lifecycle_step_id,
                        service_request_value_status,
                        primary_service_value_status, primary_service_id, issue_value_status, issue_id,
                        sentiment, operational_severity, cause_determination_status, classification_state,
                        decision_source, decision_reason, decided_by, decided_at
                    ) VALUES (
                        :decision_id, :feedback_item_id, 1, :taxonomy_release_id,
                        'KNOWN', :step_id, 'NOT_APPLICABLE',
                        'KNOWN', :service_id, :issue_status, :issue_id,
                        :sentiment, :severity, 'NOT_ASSESSED', 'ACCEPTED',
                        'SOURCE_TRUSTED', 'Direct CSV Import', UUID('00000000-0000-0000-0000-000000000002'), :reported_at
                    )
                """),
                decision_batch,
            )
            decision_batch.clear()

        if current_batch:
            await session.execute(
                text("""
                    INSERT INTO classification_current (
                        feedback_item_id, current_decision_id, current_decision_version, taxonomy_release_id,
                        customer_lifecycle_value_status, customer_lifecycle_stage_id, customer_lifecycle_step_id,
                        service_request_value_status,
                        primary_service_value_status, primary_service_id, issue_value_status, issue_id,
                        sentiment, operational_severity, cause_determination_status, classification_state,
                        last_decision_at, projection_version
                    ) VALUES (
                        :feedback_item_id, :decision_id, 1, :taxonomy_release_id,
                        'KNOWN', :stage_id, :step_id, 'NOT_APPLICABLE',
                        'KNOWN', :service_id, :issue_status, :issue_id,
                        :sentiment, :severity, 'NOT_ASSESSED', 'ACCEPTED',
                        :reported_at, 1
                    )
                """),
                current_batch,
            )
            current_batch.clear()

    for idx, row in enumerate(rows, start=1):
        content = (
            row.get("content_masked") or row.get("content_raw") or
            row.get("noi_dung") or row.get("content") or row.get("message") or
            row.get("feedback") or row.get("noidung") or row.get("review") or ""
        ).strip()
        if not content:
            continue

        # Location matching
        raw_loc_name = (
            row.get("project") or row.get("management_board") or
            row.get("khu_do_thi") or row.get("location") or row.get("khudothi") or ""
        ).strip()
        loc_code = (row.get("location_code") or row.get("building") or "").strip()
        loc_query = (raw_loc_name or loc_code).lower()
        
        matched_loc_id = None
        matched_proj_id = default_proj_id

        if loc_query:
            for l in locations:
                if l["name"] and (loc_query in l["name"].lower() or l["name"].lower() in loc_query):
                    matched_loc_id = l["location_id"]
                    break
                if l["location_code"] and loc_query == l["location_code"].lower():
                    matched_loc_id = l["location_id"]
                    break

        if not matched_loc_id and locations:
            matched_loc_id = locations[0]["location_id"]

        # Date parsing
        date_str = (
            row.get("reported_date") or row.get("thoi_gian") or row.get("reported_at") or
            row.get("actual_end") or row.get("created_at") or row.get("thoigian") or ""
        ).strip()
        reported_at = now
        if date_str:
            cleaned_date = date_str.replace("Z", "").strip()
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y",
            ):
                try:
                    dt = datetime.strptime(cleaned_date, fmt)
                    reported_at = dt.replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    pass
            else:
                try:
                    dt = datetime.fromisoformat(cleaned_date)
                    reported_at = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
                except Exception:
                    reported_at = now

        # Source record key & ticket ID
        raw_ticket_id = (
            row.get("ticket_id") or row.get("ma_phan_anh") or row.get("id") or ""
        ).strip()
        unique_key = f"{raw_ticket_id}_{uuid4().hex[:8]}" if raw_ticket_id else f"direct-{uuid4().hex[:12]}"

        # Sentiment heuristics / parsing
        sent_input = (row.get("sentiment") or "").strip().lower()
        low_content = content.lower()
        if sent_input in ["negative", "tiêu cực", "tieu cuc", "-1"]:
            sentiment = "NEGATIVE"
            severity = "SEV-2"
        elif sent_input in ["positive", "tích cực", "tich cuc", "1"]:
            sentiment = "POSITIVE"
            severity = "SEV-4"
        elif sent_input in ["neutral", "trung tính", "trung tinh", "0"]:
            sentiment = "NEUTRAL"
            severity = "SEV-4"
        elif any(w in low_content for w in ["hỏng", "kẹt", "mùi", "bẩn", "lỗi", "chậm", "kém", "bực", "tắc", "chờ", "ồn", "thất vọng", "không nhận", "rơi", "hôi", "tệ"]):
            sentiment = "NEGATIVE"
            severity = "SEV-2"
        elif any(w in low_content for w in ["tốt", "khen", "nhiệt tình", "nhanh", "hài lòng", "tuyệt vời", "chu đáo", "cảm ơn", "sạch sẽ", "đẹp"]):
            sentiment = "POSITIVE"
            severity = "SEV-4"
        else:
            sentiment = "NEUTRAL"
            severity = "SEV-4"

        # Service & Issue matching
        service_input = (row.get("service_domain") or row.get("cause_group") or "").strip().lower()
        matched_service_id = default_service_id
        if service_input:
            for s in services:
                if s["name_vi"] and (service_input in s["name_vi"].lower() or s["name_vi"].lower() in service_input):
                    matched_service_id = s["service_id"]
                    break
        if matched_service_id == default_service_id:
            # Keyword heuristics for service
            if any(w in low_content or w in service_input for w in ["kỹ thuật", "sửa", "điện", "chiếu sáng", "điều hòa", "thiết bị", "nước", "thang máy", "cửa"]):
                s_match = next((s for s in services if s["service_code"] == "SV-07"), None)
                if s_match:
                    matched_service_id = s_match["service_id"]
            elif any(w in low_content or w in service_input for w in ["bảo vệ", "an ninh", "trộm", "mất đồ", "pccc"]):
                s_match = next((s for s in services if s["service_code"] == "SV-08"), None)
                if s_match:
                    matched_service_id = s_match["service_id"]
            elif any(w in low_content or w in service_input for w in ["xe", "đỗ xe", "bãi xe", "sạc", "parking", "thẻ xe"]):
                s_match = next((s for s in services if s["service_code"] == "SV-05"), None)
                if s_match:
                    matched_service_id = s_match["service_id"]
            elif any(w in low_content or w in service_input for w in ["hợp đồng", "cskh", "chăm sóc", "cư dân", "thủ tục", "phụ lục"]):
                s_match = next((s for s in services if s["service_code"] == "SV-03"), None)
                if s_match:
                    matched_service_id = s_match["service_id"]

        issue_input = (row.get("topic") or row.get("cause_group") or "").strip().lower()
        matched_issue_id = default_issue_id
        if issue_input:
            for iss in issues:
                if iss["name_vi"] and (issue_input in iss["name_vi"].lower() or iss["name_vi"].lower() in issue_input):
                    matched_issue_id = iss["issue_id"]
                    break

        # Stage & Step matching
        row_stage = (row.get("journey_stage") or "").strip().lower()
        row_step = (row.get("journey_step") or "").strip().lower()
        matched_stage_id = default_stage_id
        matched_step_id = default_step_id

        if row_step:
            for st in all_steps:
                if st["name_vi"] and (row_step in st["name_vi"].lower() or st["name_vi"].lower() in row_step):
                    matched_step_id = st["customer_lifecycle_step_id"]
                    matched_stage_id = st["customer_lifecycle_stage_id"]
                    break

        # Mask PII
        masked_content = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", content)
        masked_content = re.sub(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)", "[PHONE]", masked_content)
        checksum = hashlib.sha256(content.encode()).hexdigest()

        feedback_id = uuid4()
        feedback_item_id = uuid4()
        decision_id = uuid4()

        feedback_batch.append({
            "feedback_id": feedback_id,
            "project_id": matched_proj_id,
            "source_record_key": unique_key,
            "external_ticket_id": raw_ticket_id or None,
            "reported_at": reported_at,
            "now": now,
            "content_raw": content,
            "content_masked": masked_content,
            "checksum": checksum,
        })

        item_batch.append({
            "feedback_item_id": feedback_item_id,
            "feedback_id": feedback_id,
            "masked_content": masked_content,
            "location_id": matched_loc_id,
        })

        if taxonomy_release_id and matched_service_id and matched_step_id:
            issue_status = "KNOWN" if matched_issue_id else "NOT_APPLICABLE"
            decision_batch.append({
                "decision_id": decision_id,
                "feedback_item_id": feedback_item_id,
                "taxonomy_release_id": taxonomy_release_id,
                "step_id": matched_step_id,
                "service_id": matched_service_id,
                "issue_status": issue_status,
                "issue_id": matched_issue_id,
                "sentiment": sentiment,
                "severity": severity,
                "reported_at": reported_at,
            })

            current_batch.append({
                "feedback_item_id": feedback_item_id,
                "decision_id": decision_id,
                "taxonomy_release_id": taxonomy_release_id,
                "stage_id": matched_stage_id,
                "step_id": matched_step_id,
                "service_id": matched_service_id,
                "issue_status": issue_status,
                "issue_id": matched_issue_id,
                "sentiment": sentiment,
                "severity": severity,
                "reported_at": reported_at,
            })

        imported_count += 1

        # Flush batch every 1000 items to keep memory footprint ultra low and DB execution super fast
        if len(feedback_batch) >= 1000:
            await flush_batches()

    # Flush remaining records
    await flush_batches()
    await session.commit()

    return {
        "success": True,
        "total_rows": len(rows),
        "imported_rows": imported_count,
        "message": f"Đã nạp thành công {imported_count} phản hồi vào hệ thống!",
    }


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
