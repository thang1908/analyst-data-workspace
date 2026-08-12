"""PostgreSQL Job Queue với cơ chế FOR UPDATE SKIP LOCKED."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class JobClaim:
    """Thông tin 1 Job đã được claim từ hàng chờ."""

    job_id: uuid.UUID
    job_type: str
    status: str
    payload: dict[str, Any]


class AsyncJobQueue:
    """
    Hàng chờ công việc ngầm dựa trên PostgreSQL.

    Dùng cơ chế FOR UPDATE SKIP LOCKED để đảm bảo nhiều Worker
    chạy song song KHÔNG bao giờ xử lý trùng cùng 1 Job.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def claim_next_import_job(self) -> JobClaim | None:
        """
        Lấy và khóa Job import tiếp theo đang chờ xử lý.

        SKIP LOCKED: Bỏ qua các row đang bị Worker khác khóa,
        đảm bảo mỗi Worker nhận 1 Job khác nhau.
        """
        sql = text("""
            SELECT id, status
            FROM import_job
            WHERE status = 'UPLOADED'
            ORDER BY created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        result = await self.session.execute(sql)
        row = result.fetchone()

        if row is None:
            return None

        return JobClaim(
            job_id=row.id,
            job_type="import",
            status=row.status,
            payload={},
        )
