"""013 — Async Job Queue.

Creates:
  - async_job  (§16.1)  — PostgreSQL-backed durable job queue

All jobs MUST be safe to retry. Workers use FOR UPDATE SKIP LOCKED.

Revision ID: 013
Revises: 012
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "013"
down_revision: str | None = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # async_job  (§16.1)                                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "async_job",
        sa.Column(
            "async_job_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "job_type",
            sa.String(64),
            nullable=False,
            comment="e.g. IMPORT_VALIDATE, IMPORT_EXECUTE, AI_PREDICT, EXPORT_GENERATE",
        ),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("payload_json", sa.JSON, nullable=False),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default="QUEUED",
            comment="QUEUED | CLAIMED | PROCESSING | COMPLETED | FAILED | CANCELLED",
        ),
        sa.Column(
            "priority",
            sa.SmallInteger,
            nullable=False,
            server_default=sa.text("0"),
            comment="Higher = processed first",
        ),
        sa.Column(
            "available_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Earliest time worker may claim this job",
        ),
        sa.Column("claimed_by", sa.String(128), nullable=True),
        sa.Column("claimed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "lease_expires_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            comment="Worker must renew or job becomes re-claimable",
        ),
        sa.Column(
            "attempt_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "max_attempts",
            sa.Integer,
            nullable=False,
            server_default=sa.text("3"),
        ),
        sa.Column("last_error_code", sa.String(64), nullable=True),
        sa.Column("last_error_message", sa.Text, nullable=True),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.CheckConstraint(
            "status IN ('QUEUED','CLAIMED','PROCESSING','COMPLETED','FAILED','CANCELLED')",
            name="ck_async_job_status",
        ),
        sa.CheckConstraint(
            "attempt_count <= max_attempts",
            name="ck_async_job_attempts",
        ),
    )

    # Index for worker polling: WHERE status='QUEUED' AND available_at <= now()
    # ORDER BY priority DESC, created_at  FOR UPDATE SKIP LOCKED
    op.create_index(
        "ix_async_job_poll",
        "async_job",
        ["status", sa.text("priority DESC"), "available_at"],
    )
    op.create_index("ix_async_job_resource", "async_job", ["resource_type", "resource_id"])
    op.create_index("ix_async_job_correlation", "async_job", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_async_job_correlation", table_name="async_job")
    op.drop_index("ix_async_job_resource", table_name="async_job")
    op.drop_index("ix_async_job_poll", table_name="async_job")
    op.drop_table("async_job")
