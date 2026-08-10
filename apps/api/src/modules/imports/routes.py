from uuid import UUID
from fastapi import APIRouter, Depends, Form, Header, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from cx_contracts.common.actor import ActorContext
from cx_contracts.import_pkg.import_job import (
    ExecuteJobRequest,
    ImportJobCreateResponse,
    ImportJobResponse,
    RetryJobRequest,
    ValidateJobRequest,
)
from cx_db.src.session import get_async_session
from apps.api.src.modules/imports.handlers import (
    handle_create_import_job,
    handle_execute_job,
    handle_get_import_job,
    handle_get_job_errors,
    handle_retry_job,
    handle_validate_job,
)

import_router = APIRouter(prefix="/api/v1/import-jobs", tags=["Import Jobs"])


async def get_actor_context(request: Request) -> ActorContext:
    """Dependency to extract ActorContext from request state or headers for testing/runtime."""
    if hasattr(request.state, "actor") and isinstance(request.state.actor, ActorContext):
        return request.state.actor

    # Default fallback actor context for development/testing
    return ActorContext(
        actor_id=request.headers.get("X-Actor-ID", "test-analyst-1"),
        permissions=["imports:write", "imports:read"],
        project_ids=[],  # empty means access to all projects in dev/test
        correlation_id=request.headers.get("X-Correlation-ID", "test-corr-id"),
    )


@import_router.post(
    "",
    response_model=ImportJobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_import_job(
    project_code: str = Form(...),
    file: UploadFile = Form(...),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_create_import_job(session, actor, project_code, file, idempotency_key)


@import_router.get(
    "/{job_id}",
    response_model=ImportJobResponse,
)
async def get_import_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_get_import_job(session, actor, job_id)


@import_router.post(
    "/{job_id}/validate",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def validate_import_job(
    job_id: UUID,
    body: ValidateJobRequest,
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_validate_job(session, actor, job_id, body)


@import_router.post(
    "/{job_id}/execute",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def execute_import_job(
    job_id: UUID,
    body: ExecuteJobRequest,
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_execute_job(session, actor, job_id, body)


@import_router.post(
    "/{job_id}/retry",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def retry_import_job(
    job_id: UUID,
    body: RetryJobRequest,
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_retry_job(session, actor, job_id, body)


@import_router.get(
    "/{job_id}/errors",
)
async def get_job_errors(
    job_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    actor: ActorContext = Depends(get_actor_context),
):
    return await handle_get_job_errors(session, actor, job_id, format, limit)
