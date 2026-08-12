"""008 — AI Prediction Ledger.

Creates:
  - prediction_run    (§9.1)
  - prediction_event  (§9.2)

Rows are append-only — no UPDATE/DELETE after insert.

Revision ID: 008
Revises: 007
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: str | None = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # prediction_run  (§9.1)                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "prediction_run",
        sa.Column(
            "prediction_run_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_pr_taxonomy_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("model_version", sa.String(128), nullable=False),
        sa.Column("pipeline_version", sa.String(128), nullable=False),
        sa.Column("prompt_or_config_hash", sa.String(128), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("requested_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("correlation_id", sa.String(128), nullable=False),
    )

    op.create_index("ix_prediction_run_project", "prediction_run", ["project_id"])
    op.create_index(
        "ix_prediction_run_release", "prediction_run", ["taxonomy_release_id"]
    )

    # ------------------------------------------------------------------ #
    # prediction_event  (§9.2)  — append-only, one row per predicted field#
    # ------------------------------------------------------------------ #
    op.create_table(
        "prediction_event",
        sa.Column(
            "prediction_event_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "prediction_run_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "prediction_run.prediction_run_id",
                name="fk_pe_run",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_pe_item",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_pe_taxonomy_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "field_name",
            sa.String(64),
            nullable=False,
            comment=(
                "P0 allowed: customer_lifecycle_step, service_request_step, "
                "primary_service, issue, sentiment"
            ),
        ),
        sa.Column("candidate_ref_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("candidate_code", sa.String(64), nullable=True),
        sa.Column("candidate_scalar", sa.String(255), nullable=True),
        sa.Column("rank", sa.SmallInteger, nullable=False),
        sa.Column(
            "confidence",
            sa.Numeric(6, 5),
            nullable=True,
            comment="0.00000–1.00000 when non-null",
        ),
        sa.Column("rationale_masked", sa.Text, nullable=True),
        sa.Column("model_payload_json", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # Constraints
        sa.UniqueConstraint(
            "prediction_run_id",
            "feedback_item_id",
            "field_name",
            "rank",
            name="uq_pe_run_item_field_rank",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_pe_confidence_range",
        ),
        sa.CheckConstraint(
            "field_name IN ('customer_lifecycle_step','service_request_step',"
            "'primary_service','issue','sentiment')",
            name="ck_pe_field_name",
        ),
    )

    op.create_index("ix_pe_run", "prediction_event", ["prediction_run_id"])
    op.create_index(
        "ix_pe_item_field_created",
        "prediction_event",
        ["feedback_item_id", "field_name", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_pe_item_field_created", table_name="prediction_event")
    op.drop_index("ix_pe_run", table_name="prediction_event")
    op.drop_table("prediction_event")

    op.drop_index("ix_prediction_run_release", table_name="prediction_run")
    op.drop_index("ix_prediction_run_project", table_name="prediction_run")
    op.drop_table("prediction_run")
