from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field

from cx_contracts.common.enums import ImportJobState
from cx_contracts.import_pkg.import_errors import ImportRowErrorDetail


class ImportJobCounts(BaseModel):
    total_rows: int = Field(default=0, ge=0)
    valid_rows: int = Field(default=0, ge=0)
    invalid_rows: int = Field(default=0, ge=0)
    duplicate_rows: int = Field(default=0, ge=0)
    committed_rows: int = Field(default=0, ge=0)


class ImportJobData(BaseModel):
    job_id: UUID
    actor_id: str
    project_id: UUID
    idempotency_key: str
    contract_version: str
    file_name: str
    file_sha256: str
    state: ImportJobState
    version: int = Field(default=1, ge=1)
    counts: ImportJobCounts | None = None
    created_at: datetime
    completed_at: datetime | None = None
    retryable: bool = False
    failure_reason: str | None = None


class ImportJobCreateData(BaseModel):
    job_id: UUID
    state: ImportJobState
    version: int = Field(default=1, ge=1)
    contract_version: str
    file_sha256: str
    counts: ImportJobCounts | None = None


class ImportJobCreateResponse(BaseModel):
    data: ImportJobCreateData
    correlation_id: str


class ImportJobResponse(BaseModel):
    data: ImportJobData
    correlation_id: str


class ValidateJobRequest(BaseModel):
    expected_version: int = Field(..., ge=1)


class ExecuteJobRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    commit_policy: Literal["VALID_ROWS_ONLY"] = "VALID_ROWS_ONLY"


class RetryJobRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    phase: Literal["VALIDATION", "EXECUTION"]


class ImportJobErrorResponse(BaseModel):
    items: list[ImportRowErrorDetail]
    total_count: int = Field(..., ge=0)
    next_cursor: str | None = None
    correlation_id: str
