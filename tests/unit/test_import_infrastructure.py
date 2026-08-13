"""Fast, isolated acceptance tests for the streaming import infrastructure."""
from __future__ import annotations

import csv
import io
from time import perf_counter
from uuid import uuid4

import pytest
from openpyxl import Workbook

from apps.worker.handlers.import_handler import ImportWorkerHandler, stream_import_rows
from packages.domain.import_pipeline.validation import validate_rows
from packages.infrastructure.storage.s3 import StoragePort


class MemoryStorage(StoragePort):
    def __init__(self) -> None:
        self.uploads: dict[str, bytes] = {}

    async def generate_presigned_url(self, object_name: str, client_action: str = "get_object", expires_in: int = 3600) -> str:
        return f"memory://{object_name}?action={client_action}&expires={expires_in}"

    async def delete_object(self, object_name: str) -> bool:
        self.uploads.pop(object_name, None)
        return True

    async def download_fileobj(self, object_name: str, destination: io.BytesIO) -> None:
        destination.write(self.uploads[object_name])
        destination.seek(0)

    async def upload_fileobj(self, object_name: str, source: io.BytesIO, *, content_type: str) -> None:
        self.uploads[object_name] = source.read()


def test_stream_csv_10k_rows_and_validate_within_five_seconds() -> None:
    source = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(source, encoding="utf-8", newline="", write_through=True))
    writer.writerow(["ticket_id", "message", "reported_date"])
    for index in range(10_000):
        writer.writerow([f"row-{index}", "Cần hỗ trợ", "2026-08-13T08:00:00Z"])
    source.seek(0)

    started = perf_counter()
    rows = stream_import_rows(source, "feedback.csv")
    validated = validate_rows(
        source_system="resident-app",
        mapping={"ticket_id": "source_record_key", "message": "content", "reported_date": "reported_at"},
        raw_rows=rows,
    )

    assert len(validated) == 10_000
    assert all(row.is_valid for row in validated)
    assert perf_counter() - started < 5


def test_stream_xlsx_rows_in_read_only_format() -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["ticket_id", "message"])
    worksheet.append(["ticket-1", "Nội dung phản hồi"])
    source = io.BytesIO()
    workbook.save(source)

    assert list(stream_import_rows(source, "feedback.xlsx")) == [
        {"ticket_id": "ticket-1", "message": "Nội dung phản hồi"}
    ]


@pytest.mark.asyncio
async def test_error_report_is_downloadable_and_excludes_raw_feedback() -> None:
    storage = MemoryStorage()
    handler = ImportWorkerHandler(repository=object(), storage=storage)  # type: ignore[arg-type]
    job_id = uuid4()

    object_key = await handler._upload_error_report(  # noqa: SLF001 - acceptance test
        job_id,
        [{
            "row_number": 4,
            "source_record_key": "ticket-4",
            "field_name": "content",
            "error_code": "REQUIRED_FIELD",
            "message": "Feedback content is required.",
            "severity": "ERROR",
            "content": "must never be exported",
        }],
    )

    assert object_key == f"imports/{job_id}/error_report.csv"
    report = storage.uploads[object_key].decode()
    assert "ticket-4" in report
    assert "REQUIRED_FIELD" in report
    assert "must never be exported" not in report
