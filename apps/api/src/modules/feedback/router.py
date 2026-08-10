from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Query, status

from cx_contracts.feedback.models import (
    FeedbackItemDetailDTO,
    FeedbackItemListResponse,
    FeedbackItemSummaryDTO,
    ProvenanceDTO,
)

feedback_router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback Drill-down"])

# Mock feedback items generator
SAMPLE_ITEMS = [
    FeedbackItemSummaryDTO(
        feedback_item_id=UUID("98214000-0000-0000-0000-000000098214"),
        created_at=datetime(2026, 8, 10, 14, 20, 0),
        service_name="Customer Support",
        issue_name="Slow Response Time",
        location_name="Building A - Floor 3",
        sentiment="NEGATIVE",
        severity="SEV-2",
        masked_text="Khách hàng phản ánh nhân viên *** chậm trễ hỗ trợ xử lý sự cố.",
    ),
    FeedbackItemSummaryDTO(
        feedback_item_id=UUID("98215000-0000-0000-0000-000000098215"),
        created_at=datetime(2026, 8, 10, 13, 5, 0),
        service_name="Billing Services",
        issue_name="Payment Failed",
        location_name="Building B - Floor 1",
        sentiment="NEGATIVE",
        severity="SEV-1",
        masked_text="Thanh toán hóa đơn qua cổng *** bị lỗi nhưng vẫn trừ tiền tài khoản.",
    ),
    FeedbackItemSummaryDTO(
        feedback_item_id=UUID("98216000-0000-0000-0000-000000098216"),
        created_at=datetime(2026, 8, 10, 11, 45, 0),
        service_name="Product Features",
        issue_name="Slow Response Time",
        location_name="Building A - Floor 5",
        sentiment="POSITIVE",
        severity="SEV-4",
        masked_text="Giao diện mới nâng cấp rất dễ sử dụng và phản hồi nhanh chóng.",
    ),
]


@feedback_router.get("/items", response_model=FeedbackItemListResponse)
async def list_feedback_items(
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    service_code: Optional[list[str]] = Query(None),
    sentiment: Optional[list[str]] = Query(None),
) -> FeedbackItemListResponse:
    filtered = SAMPLE_ITEMS
    if sentiment:
        filtered = [item for item in filtered if item.sentiment in sentiment]

    return FeedbackItemListResponse(
        items=filtered[:limit],
        next_cursor=None,
        has_more=False,
        total_matching=len(filtered),
    )


@feedback_router.get("/items/{item_id}", response_model=FeedbackItemDetailDTO)
async def get_feedback_item_detail(item_id: UUID) -> FeedbackItemDetailDTO:
    for item in SAMPLE_ITEMS:
        if item.feedback_item_id == item_id:
            return FeedbackItemDetailDTO(
                feedback_item_id=item.feedback_item_id,
                created_at=item.created_at,
                service_name=item.service_name,
                issue_name=item.issue_name,
                location_name=item.location_name,
                sentiment=item.sentiment,
                severity=item.severity,
                masked_text=item.masked_text,
                provenance=ProvenanceDTO(
                    import_job_id=UUID("9842a1b7-0000-0000-0000-000000000000"),
                    source_reference="feedback_july_batch.csv",
                    row_index=42,
                    decision="SOURCE_TRUSTED",
                    committed_at=datetime(2026, 8, 10, 14, 5, 0),
                ),
            )

    # Default fallback for unlisted IDs in mock demo
    return FeedbackItemDetailDTO(
        feedback_item_id=item_id,
        created_at=datetime.utcnow(),
        service_name="Customer Support",
        issue_name="Slow Response Time",
        location_name="Building A - Floor 3",
        sentiment="NEGATIVE",
        severity="SEV-2",
        masked_text="Nội dung phản ánh đã được mã hóa PII an toàn...",
        provenance=ProvenanceDTO(
            import_job_id=UUID("9842a1b7-0000-0000-0000-000000000000"),
            source_reference="feedback_july_batch.csv",
            row_index=1,
            decision="SOURCE_TRUSTED",
            committed_at=datetime.utcnow(),
        ),
    )
