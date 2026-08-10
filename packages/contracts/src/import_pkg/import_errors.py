from enum import Enum
from pydantic import BaseModel, Field


class ImportErrorCode(str, Enum):
    INVALID_ENCODING = "INVALID_ENCODING"
    INVALID_CSV_SYNTAX = "INVALID_CSV_SYNTAX"
    INVALID_HEADER = "INVALID_HEADER"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    ROW_LIMIT_EXCEEDED = "ROW_LIMIT_EXCEEDED"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    VALUE_TOO_LONG = "VALUE_TOO_LONG"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    PROJECT_SCOPE_MISMATCH = "PROJECT_SCOPE_MISMATCH"
    UNKNOWN_PROJECT = "UNKNOWN_PROJECT"
    UNKNOWN_LOCATION = "UNKNOWN_LOCATION"
    UNKNOWN_SERVICE = "UNKNOWN_SERVICE"
    UNKNOWN_ISSUE = "UNKNOWN_ISSUE"
    INVALID_SERVICE_ISSUE = "INVALID_SERVICE_ISSUE"
    INVALID_SENTIMENT = "INVALID_SENTIMENT"
    INVALID_SEVERITY = "INVALID_SEVERITY"
    DUPLICATE_IN_FILE = "DUPLICATE_IN_FILE"
    DUPLICATE_SOURCE_REFERENCE = "DUPLICATE_SOURCE_REFERENCE"


class ImportRowErrorDetail(BaseModel):
    row_number: int = Field(..., description="1-indexed row number")
    column: str | None = Field(default=None, description="Column name if applicable")
    code: ImportErrorCode = Field(..., description="Stable error code")
    message: str = Field(..., description="Safe human-readable error message")
    duplicate_reference: str | None = Field(default=None, description="Reference key of duplicate if applicable")
