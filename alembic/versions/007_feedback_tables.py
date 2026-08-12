"""007 — Feedback tables.

Creates:
  - feedback                        (§8.1)
  - feedback_item                   (§8.2)
  - feedback_item_affected_channel  (§8.3)

Also adds deferred FK from import_row.feedback_id → feedback.feedback_id.

Revision ID: 007
Revises: 006
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: str | None = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # feedback  (§8.1)  — immutable source envelope                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "feedback",
        sa.Column(
            "feedback_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system", sa.String(128), nullable=False),
        sa.Column("source_record_key", sa.String(255), nullable=True),
        sa.Column(
            "intake_channel_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "interaction_channel.interaction_channel_id",
                name="fk_feedback_intake_channel",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("external_ticket_id", sa.String(255), nullable=True),
        sa.Column("reported_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "ingested_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "content_raw",
            sa.Text,
            nullable=False,
            comment="Immutable privileged content — never exposed in analytics",
        ),
        sa.Column("content_masked", sa.Text, nullable=False),
        sa.Column("source_metadata_json", sa.JSON, nullable=True),
        sa.Column(
            "import_job_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "import_job.import_job_id",
                name="fk_feedback_import_job",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column(
            "import_row_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "import_row.import_row_id",
                name="fk_feedback_import_row",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column("raw_content_checksum", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # Constraints
        sa.UniqueConstraint(
            "source_system",
            "source_record_key",
            name="uq_feedback_source_key",
        ),
    )

    op.create_index(
        "ix_feedback_project_reported",
        "feedback",
        ["project_id", sa.text("reported_at DESC")],
    )
    op.create_index(
        "ix_feedback_source",
        "feedback",
        ["source_system", "source_record_key"],
    )
    op.create_index("ix_feedback_checksum", "feedback", ["raw_content_checksum"])

    # Now that feedback exists, add FK on import_row.feedback_id
    op.create_foreign_key(
        "fk_import_row_feedback",
        "import_row",
        "feedback",
        ["feedback_id"],
        ["feedback_id"],
        ondelete="RESTRICT",
    )

    # ------------------------------------------------------------------ #
    # feedback_item  (§8.2)  — atomic analytic unit                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "feedback_item",
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "feedback_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback.feedback_id",
                name="fk_fi_feedback",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("item_index", sa.SmallInteger, nullable=False),
        sa.Column(
            "parent_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_fi_parent",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column(
            "item_text_masked",
            sa.Text,
            nullable=False,
            comment="Text used for AI and review — may differ from content_masked after split",
        ),
        sa.Column("symptom_detail", sa.Text, nullable=True),
        sa.Column(
            "location_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "location.location_id",
                name="fk_fi_location",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default="ACTIVE",
            comment="feedback_item_status: ACTIVE | SPLIT_PARENT | RETIRED",
        ),
        sa.Column(
            "analytic_eligibility",
            sa.Text,
            nullable=False,
            server_default="PENDING",
            comment="analytic_eligibility: INCLUDED | EXCLUDED | PENDING",
        ),
        sa.Column("eligibility_reason", sa.Text, nullable=True),
        sa.Column(
            "split_source",
            sa.String(32),
            nullable=True,
            comment="HUMAN or SYSTEM",
        ),
        sa.Column("split_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("split_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.UniqueConstraint(
            "feedback_id", "item_index", name="uq_fi_feedback_index"
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE','SPLIT_PARENT','RETIRED')",
            name="ck_fi_status",
        ),
        sa.CheckConstraint(
            "analytic_eligibility IN ('INCLUDED','EXCLUDED','PENDING')",
            name="ck_fi_analytic_eligibility",
        ),
        sa.CheckConstraint(
            "split_source IS NULL OR split_source IN ('HUMAN','SYSTEM')",
            name="ck_fi_split_source",
        ),
    )

    op.create_index("ix_fi_feedback", "feedback_item", ["feedback_id"])
    op.create_index("ix_fi_location", "feedback_item", ["location_id"])
    op.create_index(
        "ix_fi_status_eligibility",
        "feedback_item",
        ["status", "analytic_eligibility"],
    )

    # ------------------------------------------------------------------ #
    # feedback_item_affected_channel  (§8.3)                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "feedback_item_affected_channel",
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_fiac_item",
                ondelete="CASCADE",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "interaction_channel_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "interaction_channel.interaction_channel_id",
                name="fk_fiac_channel",
                ondelete="RESTRICT",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "ix_fiac_item", "feedback_item_affected_channel", ["feedback_item_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_fiac_item", table_name="feedback_item_affected_channel")
    op.drop_table("feedback_item_affected_channel")

    op.drop_index("ix_fi_status_eligibility", table_name="feedback_item")
    op.drop_index("ix_fi_location", table_name="feedback_item")
    op.drop_index("ix_fi_feedback", table_name="feedback_item")
    op.drop_table("feedback_item")

    op.drop_constraint("fk_import_row_feedback", "import_row", type_="foreignkey")

    op.drop_index("ix_feedback_checksum", table_name="feedback")
    op.drop_index("ix_feedback_source", table_name="feedback")
    op.drop_index("ix_feedback_project_reported", table_name="feedback")
    op.drop_table("feedback")
