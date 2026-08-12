"""010 — Classification Current Projection.

Creates:
  - classification_current                (§10.5)
  - classification_current_candidate_cause (§10.6)

These are rebuildable read projections — NOT source of truth.
Source of truth is classification_decision.

Revision ID: 010
Revises: 009
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: str | None = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # classification_current  (§10.5)  — 1:1 projection per feedback_item#
    # ------------------------------------------------------------------ #
    op.create_table(
        "classification_current",
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_cc_item",
                ondelete="CASCADE",
            ),
            nullable=False,
            primary_key=True,
            comment="PK and FK — 1:1 with feedback_item",
        ),
        sa.Column(
            "current_decision_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_decision.classification_decision_id",
                name="fk_cc_decision",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("current_decision_version", sa.Integer, nullable=False),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_cc_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        # Customer lifecycle
        sa.Column("customer_lifecycle_value_status", sa.String(16), nullable=False),
        sa.Column(
            "customer_lifecycle_stage_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "customer_lifecycle_stage.customer_lifecycle_stage_id",
                name="fk_cc_cl_stage",
                ondelete="RESTRICT",
            ),
            nullable=True,
            comment="Derived from step; never separately decided",
        ),
        sa.Column(
            "customer_lifecycle_step_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "customer_lifecycle_step.customer_lifecycle_step_id",
                name="fk_cc_cl_step",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        # Service request lifecycle
        sa.Column("service_request_value_status", sa.String(16), nullable=False),
        sa.Column(
            "service_request_step_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service_request_step.service_request_step_id",
                name="fk_cc_sr_step",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        # Primary service
        sa.Column("primary_service_value_status", sa.String(16), nullable=False),
        sa.Column(
            "primary_service_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service.service_id",
                name="fk_cc_service",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        # Issue
        sa.Column("issue_value_status", sa.String(16), nullable=False),
        sa.Column(
            "issue_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "issue.issue_id",
                name="fk_cc_issue",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        # Scalar fields
        sa.Column("sentiment", sa.String(16), nullable=False),
        sa.Column("operational_severity", sa.String(8), nullable=False),
        sa.Column("cause_determination_status", sa.String(32), nullable=False),
        sa.Column("other_reason", sa.Text, nullable=True),
        sa.Column("classification_state", sa.String(32), nullable=False),
        sa.Column("last_decision_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("projection_version", sa.Integer, nullable=False),
        sa.Column("rebuilt_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.UniqueConstraint("current_decision_id", name="uq_cc_current_decision"),
    )

    # Analytics query indexes (§18)
    op.create_index(
        "ix_cc_service_issue", "classification_current", ["primary_service_id", "issue_id"]
    )
    op.create_index(
        "ix_cc_cl_step", "classification_current", ["customer_lifecycle_step_id"]
    )
    op.create_index(
        "ix_cc_sr_step", "classification_current", ["service_request_step_id"]
    )
    op.create_index("ix_cc_sentiment", "classification_current", ["sentiment"])
    op.create_index(
        "ix_cc_severity", "classification_current", ["operational_severity"]
    )
    op.create_index(
        "ix_cc_last_decision_at",
        "classification_current",
        [sa.text("last_decision_at DESC")],
    )

    # ------------------------------------------------------------------ #
    # classification_current_candidate_cause  (§10.6)                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "classification_current_candidate_cause",
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_current.feedback_item_id",
                name="fk_cccc_current",
                ondelete="CASCADE",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "cause_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "cause.cause_id",
                name="fk_cccc_cause",
                ondelete="RESTRICT",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("rank", sa.SmallInteger, nullable=False),
        sa.Column("confidence", sa.Numeric(6, 5), nullable=True),
        sa.Column(
            "current_decision_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_decision.classification_decision_id",
                name="fk_cccc_decision",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("projection_version", sa.Integer, nullable=False),
    )

    op.create_index(
        "ix_cccc_item", "classification_current_candidate_cause", ["feedback_item_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_cccc_item", table_name="classification_current_candidate_cause")
    op.drop_table("classification_current_candidate_cause")

    op.drop_index("ix_cc_last_decision_at", table_name="classification_current")
    op.drop_index("ix_cc_severity", table_name="classification_current")
    op.drop_index("ix_cc_sentiment", table_name="classification_current")
    op.drop_index("ix_cc_sr_step", table_name="classification_current")
    op.drop_index("ix_cc_cl_step", table_name="classification_current")
    op.drop_index("ix_cc_service_issue", table_name="classification_current")
    op.drop_table("classification_current")
