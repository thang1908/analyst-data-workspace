import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator

from cx_contracts.common.enums import Sentiment, Severity

TRUSTED_CSV_V1_CONTRACT_VERSION = "trusted-feedback-csv/v1"

EXACT_CSV_V1_HEADERS = [
    "source_reference",
    "reported_at",
    "project_code",
    "location_code",
    "service_code",
    "issue_code",
    "sentiment",
    "operational_severity",
    "content_masked",
]

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MiB
MAX_ROW_COUNT = 10_000
MAX_CONTENT_LENGTH = 4_000


class CSVRowV1(BaseModel):
    source_reference: str = Field(..., max_length=255)
    reported_at: datetime
    project_code: str = Field(..., max_length=64)
    location_code: str = Field(..., max_length=64)
    service_code: str = Field(..., max_length=64)
    issue_code: str = Field(..., max_length=64)
    sentiment: Sentiment
    operational_severity: Severity
    content_masked: str = Field(..., max_length=4000)

    @field_validator("source_reference", "project_code", "location_code", "service_code", "issue_code", mode="before")
    @classmethod
    def trim_whitespace(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("content_masked", mode="before")
    @classmethod
    def normalize_newlines(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.replace("\r\n", "\n").replace("\r", "\n")
        return v


def compute_row_checksum(row_dict: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 checksum for normalized CSV row dictionary."""
    canonical_json = json.dumps(row_dict, sort_keys=True, default=str)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def escape_spreadsheet_formula(cell_value: str) -> str:
    """Escape cell value for CSV export to prevent formula injection ('=, '+, '-, '@)."""
    if cell_value and cell_value[0] in ("=", "+", "-", "@"):
        return "'" + cell_value
    return cell_value
