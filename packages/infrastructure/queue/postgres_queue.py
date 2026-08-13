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

    async_job_id: uuid.UUID
    job_type: str
    status: str
    payload: dict[str, Any]
    resource_id: uuid.UUID | None

    @property
    def job_id(self) -> uuid.UUID:
        """Compatibility alias for the durable async-job identifier."""
        return self.async_job_id


class AsyncJobQueue:
    """
    Hàng chờ công việc ngầm dựa trên PostgreSQL.

    Dùng cơ chế FOR UPDATE SKIP LOCKED để đảm bảo nhiều Worker
    chạy song song KHÔNG bao giờ xử lý trùng cùng 1 Job.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def claim_next_import_job(self, worker_id: str) -> JobClaim | None:
        """
        Lấy và khóa Job import tiếp theo đang chờ xử lý.

        SKIP LOCKED: Bỏ qua các row đang bị Worker khác khóa,
        đảm bảo mỗi Worker nhận 1 Job khác nhau.
        """
        sql = text("""
            WITH next_job AS (
                SELECT async_job_id
                FROM async_job
                WHERE status = 'QUEUED'
                  AND job_type IN ('IMPORT_VALIDATE', 'IMPORT_EXECUTE')
                  AND available_at <= now()
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            UPDATE async_job AS job
            SET status = 'CLAIMED',
                claimed_by = :worker_id,
                claimed_at = now(),
                lease_expires_at = now() + interval '5 minutes',
                attempt_count = attempt_count + 1
            FROM next_job
            WHERE job.async_job_id = next_job.async_job_id
            RETURNING job.async_job_id, job.job_type, job.status, job.payload_json, job.resource_id
        """)
        result = await self.session.execute(sql, {"worker_id": worker_id})
        row = result.fetchone()

        if row is None:
            return None

        return JobClaim(
            async_job_id=row.async_job_id,
            job_type=row.job_type,
            status=row.status,
            payload=dict(row.payload_json or {}),
            resource_id=row.resource_id,
        )

    async def mark_completed(self, async_job_id: uuid.UUID) -> None:
        await self.session.execute(
            text("""
                UPDATE async_job
                SET status = 'COMPLETED', completed_at = now(), lease_expires_at = NULL
                WHERE async_job_id = :async_job_id AND status IN ('CLAIMED', 'PROCESSING')
            """),
            {"async_job_id": async_job_id},
        )

    async def mark_failed(self, async_job_id: uuid.UUID, *, error_code: str, message: str) -> None:
        """Record a bounded operational error; callers must never pass raw row content."""
        await self.session.execute(
            text("""
                UPDATE async_job
                SET status = CASE WHEN attempt_count >= max_attempts THEN 'FAILED' ELSE 'QUEUED' END,
                    available_at = CASE WHEN attempt_count >= max_attempts THEN available_at
                                        ELSE now() + interval '30 seconds' END,
                    lease_expires_at = NULL,
                    last_error_code = :error_code,
                    last_error_message = :message
                WHERE async_job_id = :async_job_id
            """),
            {"async_job_id": async_job_id, "error_code": error_code, "message": message[:1000]},
        )
