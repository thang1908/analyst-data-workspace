"""Request/response contracts for asynchronous file import."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ImportAPIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ImportJobData(ImportAPIModel):
    import_job_id: UUID
    status: str
    filename: str
    file_size_bytes: int
    total_rows: int | None
    valid_rows: int | None
    invalid_rows: int | None
    committed_rows: int | None
    error_object_key: str | None = None
    created_at: datetime
    version: int


class ImportJobResponse(ImportAPIModel):
    data: ImportJobData


class MappingRequest(ImportAPIModel):
    expected_version: int = Field(ge=1)
    mapping: dict[str, str] = Field(min_length=1)


class ExecuteImportRequest(ImportAPIModel):
    expected_version: int = Field(ge=1)
    allow_partial: bool = True


class AsyncImportResponse(ImportAPIModel):
    data: ImportJobData
    async_job_id: UUID
