"""006 — Import tables.

Creates:
  - import_mapping_profile  (§7.2)
  - import_job              (§7.1)  — depends on import_mapping_profile
  - import_row              (§7.3)  — depends on import_job
  - import_row_error        (§7.4)  — depends on import_row

Revision ID: 006
Revises: 005
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # import_mapping_profile  (§7.2)                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "import_mapping_profile",
        sa.Column(
            "import_mapping_profile_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_system", sa.String(128), nullable=False),
        sa.Column("mapping_json", sa.JSON, nullable=False),
        sa.Column("normalization_json", sa.JSON, nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_imp_profile_project", "import_mapping_profile", ["project_id"])

    # ------------------------------------------------------------------ #
    # import_job  (§7.1)                                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "import_job",
        sa.Column(
            "import_job_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system", sa.String(128), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("object_key", sa.Text, nullable=False),
        sa.Column("file_checksum", sa.String(128), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default="UPLOADED",
            comment="import_job_status enum value",
        ),
        sa.Column(
            "mapping_profile_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "import_mapping_profile.import_mapping_profile_id",
                name="fk_import_job_profile",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("total_rows", sa.Integer, nullable=True),
        sa.Column("valid_rows", sa.Integer, nullable=True),
        sa.Column("invalid_rows", sa.Integer, nullable=True),
        sa.Column("committed_rows", sa.Integer, nullable=True),
        sa.Column("error_object_key", sa.Text, nullable=True),
        sa.Column("requested_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column(
            "version",
            sa.Integer,
            nullable=False,
            server_default=sa.text("1"),
            comment="Optimistic concurrency version",
        ),
        # Status check
        sa.CheckConstraint(
            "status IN ('UPLOADED','MAPPED','VALIDATING','VALIDATED','QUEUED',"
            "'PROCESSING','COMPLETED','PARTIAL','FAILED','CANCELLING','CANCELLED')",
            name="ck_import_job_status",
        ),
    )
    op.create_index(
        "ix_import_job_project_created",
        "import_job",
        ["project_id", sa.text("created_at DESC")],
    )
    op.create_index("ix_import_job_status", "import_job", ["status", "created_at"])
    op.create_index("ix_import_job_checksum", "import_job", ["file_checksum"])

    # ------------------------------------------------------------------ #
    # import_row  (§7.3)                                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "import_row",
        sa.Column(
            "import_row_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "import_job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "import_job.import_job_id",
                name="fk_import_row_job",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("row_number", sa.Integer, nullable=False),
        sa.Column("source_record_key", sa.String(255), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("raw_row_json", sa.JSON, nullable=True),
        sa.Column("normalized_row_json", sa.JSON, nullable=True),
        sa.Column("validation_status", sa.String(32), nullable=False),
        sa.Column("commit_status", sa.String(32), nullable=False),
        # feedback_id FK is added in migration 007 after feedback table exists
        sa.Column("feedback_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("committed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.UniqueConstraint(
            "import_job_id", "row_number", name="uq_import_row_job_number"
        ),
        sa.UniqueConstraint(
            "import_job_id", "idempotency_key", name="uq_import_row_job_idempotency"
        ),
    )
    op.create_index("ix_import_row_job", "import_row", ["import_job_id"])

    # ------------------------------------------------------------------ #
    # import_row_error  (§7.4)                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "import_row_error",
        sa.Column(
            "import_row_error_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "import_row_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "import_row.import_row_id",
                name="fk_import_row_error_row",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("field_name", sa.String(128), nullable=True),
        sa.Column("error_code", sa.String(64), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_import_row_error_row", "import_row_error", ["import_row_id"])


def downgrade() -> None:
    op.drop_index("ix_import_row_error_row", table_name="import_row_error")
    op.drop_table("import_row_error")

    op.drop_index("ix_import_row_job", table_name="import_row")
    op.drop_table("import_row")

    op.drop_index("ix_import_job_checksum", table_name="import_job")
    op.drop_index("ix_import_job_status", table_name="import_job")
    op.drop_index("ix_import_job_project_created", table_name="import_job")
    op.drop_table("import_job")

    op.drop_index("ix_imp_profile_project", table_name="import_mapping_profile")
    op.drop_table("import_mapping_profile")
