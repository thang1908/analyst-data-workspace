from typing import Any, Optional
from pydantic import BaseModel, Field


class FieldError(BaseModel):
    path: str = Field(..., description="Field JSON path or field name")
    code: str = Field(..., description="Error classification code")
    message: str = Field(..., description="Safe human-readable error description")


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank", description="URI reference identifying problem type")
    title: str = Field(..., description="Short, human-readable summary of problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(None, description="URI reference identifying specific occurrence")
    code: str = Field(..., description="Machine-readable error code")
    correlation_id: str = Field(..., description="Tracing correlation ID")
    field_errors: Optional[list[FieldError]] = Field(None, description="Detailed field-level validation errors")
