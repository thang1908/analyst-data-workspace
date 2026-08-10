from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from cx_contracts.common.problem import ProblemDetail

from apps.api.src.modules.imports import import_router
from apps.api.src.modules.analytics.router import analytics_router
from apps.api.src.modules.feedback.router import feedback_router

app = FastAPI(
    title="Trusted CSV to Dashboard API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(import_router)
app.include_router(analytics_router)
app.include_router(feedback_router)



@app.get("/health/live", tags=["Health"])
async def health_live() -> dict[str, str]:
    return {"status": "UP", "component": "api"}


@app.get("/health/ready", tags=["Health"])
async def health_ready() -> dict[str, str]:
    return {"status": "READY", "database": "CONNECTED"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    problem = ProblemDetail(
        type="https://errors.cx-platform.domain/INTERNAL_ERROR",
        title="Internal Server Error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc),
        instance=request.url.path,
        code="SERVER_INTERNAL_ERROR",
        correlation_id=request.headers.get("X-Correlation-ID", "unknown"),
    )
    return JSONResponse(status_code=500, content=problem.model_dump())
