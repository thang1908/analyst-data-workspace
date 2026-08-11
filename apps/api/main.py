from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from packages.infrastructure.logging import setup_logging

setup_logging()

app = FastAPI(
    title="CX Journey, Service & Root Cause Intelligence Platform API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "cx-api"}


@app.get("/api/v1/health", tags=["Health"])
async def api_health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "v1"}
