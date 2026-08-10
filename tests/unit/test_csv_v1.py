from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from cx_contracts.common.enums import Sentiment, Severity
from cx_contracts.import_pkg.csv_v1 import (
    EXACT_CSV_V1_HEADERS,
    TRUSTED_CSV_V1_CONTRACT_VERSION,
    CSVRowV1,
    compute_row_checksum,
    escape_spreadsheet_formula,
)


def test_headers_and_contract_version():
    assert TRUSTED_CSV_V1_CONTRACT_VERSION == "trusted-feedback-csv/v1"
    assert len(EXACT_CSV_V1_HEADERS) == 9
    assert EXACT_CSV_V1_HEADERS[0] == "source_reference"
    assert EXACT_CSV_V1_HEADERS[-1] == "content_masked"


def test_csv_row_v1_valid():
    now_str = "2026-08-10T12:00:00+07:00"
    row = CSVRowV1(
        source_reference="  REF-12345  ",
        reported_at=datetime.fromisoformat(now_str),
        project_code="PROJ-01",
        location_code="LOC-A",
        service_code="SVC-01",
        issue_code="ISS-01",
        sentiment=Sentiment.NEGATIVE,
        operational_severity=Severity.SEV2,
        content_masked="  Some feedback text \r\n line 2  ",
    )
    assert row.source_reference == "REF-12345"  # stripped
    assert row.content_masked == "  Some feedback text \n line 2  "  # CRLF normalized
    assert row.sentiment == Sentiment.NEGATIVE
    assert row.operational_severity == Severity.SEV2


def test_formula_escaping():
    assert escape_spreadsheet_formula("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert escape_spreadsheet_formula("+12345") == "'+12345"
    assert escape_spreadsheet_formula("-12345") == "'-12345"
    assert escape_spreadsheet_formula("@admin") == "'@admin"
    assert escape_spreadsheet_formula("Normal text") == "Normal text"


def test_row_checksum_deterministic():
    payload1 = {"b": "2", "a": "1"}
    payload2 = {"a": "1", "b": "2"}
    assert compute_row_checksum(payload1) == compute_row_checksum(payload2)
