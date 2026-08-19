"""FastAPI router for AI classification endpoints."""
from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.ai import (
    AIClassificationPipeline,
    BatchClassificationInput,
    BatchClassificationOutput,
    FeedbackClassifier,
)
from packages.infrastructure.db.session import AsyncSessionLocal

router = APIRouter(prefix="/api/v1/ai", tags=["AI Classification"])


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/classify", response_model=BatchClassificationOutput)
async def classify_feedback_items(
    payload: BatchClassificationInput,
) -> BatchClassificationOutput:
    """Classify a list of feedback text items using LangChain structured output."""
    classifier = FeedbackClassifier()
    return await classifier.classify_batch(payload.items)


@router.post("/classify-project/{project_id}")
async def classify_project_items(
    project_id: UUID,
    session: SessionDep,
    limit: int = Query(100, ge=1, le=1000),
    batch_size: int = Query(25, ge=1, le=50),
) -> dict[str, Any]:
    """Execute AI classification on pending database feedback records for a project."""
    pipeline = AIClassificationPipeline(session)
    stats = await pipeline.run_batch_classification(
        project_id, limit=limit, batch_size=batch_size
    )
    return {
        "success": True,
        "project_id": str(project_id),
        "stats": stats,
        "message": f"Đã phân loại AI thành công cho {stats['classified']} phản hồi!",
    }
