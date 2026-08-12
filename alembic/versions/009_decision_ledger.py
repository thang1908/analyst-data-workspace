"""009 — Decision Ledger.

Creates:
  - classification_decision                    (§10.1)
  - classification_decision_candidate_cause    (§10.2)
  - classification_decision_prediction_ref     (§10.3)
  - review_event                               (§10.4)

All ledger tables are append-only after commit.

Revision ID: 009
Revises: 008
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: str | None = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # classification_decision  (§10.1)                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "classification_decision",
        sa.Column(
            "classification_decision_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_cd_item",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "decision_version",
            sa.Integer,
            nullable=False,
            comment="Monotonically increasing per feedback_item",
        ),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_cd_taxonomy_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        # Customer lifecycle
        sa.Column(
            "customer_lifecycle_value_status",
            sa.String(16),
            nullable=False,
            comment="value_status",
        ),
        sa.Column(
            "customer_lifecycle_step_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "customer_lifecycle_step.customer_lifecycle_step_id",
                name="fk_cd_cl_step",
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
                name="fk_cd_sr_step",
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
                name="fk_cd_service",
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
                name="fk_cd_issue",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        # Scalar fields
        sa.Column("sentiment", sa.String(16), nullable=False),
        sa.Column("operational_severity", sa.String(8), nullable=False),
        sa.Column("cause_determination_status", sa.String(32), nullable=False),
        sa.Column(
            "other_reason",
            sa.Text,
            nullable=True,
            comment="Mandatory when service is SV-10 or issue IS-10-01",
        ),
        sa.Column("classification_state", sa.String(32), nullable=False),
        sa.Column("decision_source", sa.String(32), nullable=False),
        sa.Column("decision_reason", sa.Text, nullable=True),
        sa.Column("decided_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("decided_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # Constraints
        sa.UniqueConstraint(
            "feedback_item_id",
            "decision_version",
            name="uq_cd_item_version",
        ),
        sa.CheckConstraint(
            "customer_lifecycle_value_status IN ('KNOWN','UNKNOWN','MISSING','NOT_APPLICABLE')",
            name="ck_cd_cl_value_status",
        ),
        sa.CheckConstraint(
            "service_request_value_status IN ('KNOWN','UNKNOWN','MISSING','NOT_APPLICABLE')",
            name="ck_cd_sr_value_status",
        ),
        sa.CheckConstraint(
            "primary_service_value_status IN ('KNOWN','UNKNOWN','MISSING','NOT_APPLICABLE')",
            name="ck_cd_ps_value_status",
        ),
        sa.CheckConstraint(
            "issue_value_status IN ('KNOWN','UNKNOWN','MISSING','NOT_APPLICABLE')",
            name="ck_cd_issue_value_status",
        ),
        sa.CheckConstraint(
            "sentiment IN ('POSITIVE','NEUTRAL','NEGATIVE','UNKNOWN')",
            name="ck_cd_sentiment",
        ),
        sa.CheckConstraint(
            "operational_severity IN ('SEV-1','SEV-2','SEV-3','SEV-4')",
            name="ck_cd_severity",
        ),
        sa.CheckConstraint(
            "cause_determination_status IN ('NOT_ASSESSED','UNKNOWN','SUGGESTED',"
            "'UNDER_INVESTIGATION','CONFIRMED','NOT_APPLICABLE')",
            name="ck_cd_cause_det_status",
        ),
        sa.CheckConstraint(
            "classification_state IN ('PENDING_REVIEW','ACCEPTED','REJECTED','SUPERSEDED')",
            name="ck_cd_state",
        ),
        sa.CheckConstraint(
            "decision_source IN ('MANUAL','SOURCE_TRUSTED','HUMAN_ACCEPTED_AI',"
            "'HUMAN_CORRECTED_AI','POLICY_AUTO_APPLIED','SYSTEM_MIGRATION')",
            name="ck_cd_source",
        ),
        # value_status / FK nullability rules (app-enforced by domain, DB-level guard):
        # KNOWN → FK must not be null
        sa.CheckConstraint(
            "customer_lifecycle_value_status != 'KNOWN' OR customer_lifecycle_step_id IS NOT NULL",
            name="ck_cd_cl_known_fk",
        ),
        sa.CheckConstraint(
            "customer_lifecycle_value_status = 'KNOWN' OR customer_lifecycle_step_id IS NULL",
            name="ck_cd_cl_nonknown_fk",
        ),
        sa.CheckConstraint(
            "service_request_value_status != 'KNOWN' OR service_request_step_id IS NOT NULL",
            name="ck_cd_sr_known_fk",
        ),
        sa.CheckConstraint(
            "service_request_value_status = 'KNOWN' OR service_request_step_id IS NULL",
            name="ck_cd_sr_nonknown_fk",
        ),
        sa.CheckConstraint(
            "primary_service_value_status != 'KNOWN' OR primary_service_id IS NOT NULL",
            name="ck_cd_ps_known_fk",
        ),
        sa.CheckConstraint(
            "primary_service_value_status = 'KNOWN' OR primary_service_id IS NULL",
            name="ck_cd_ps_nonknown_fk",
        ),
        sa.CheckConstraint(
            "issue_value_status != 'KNOWN' OR issue_id IS NOT NULL",
            name="ck_cd_issue_known_fk",
        ),
        sa.CheckConstraint(
            "issue_value_status = 'KNOWN' OR issue_id IS NULL",
            name="ck_cd_issue_nonknown_fk",
        ),
    )

    op.create_index(
        "ix_cd_item_version",
        "classification_decision",
        ["feedback_item_id", sa.text("decision_version DESC")],
    )
    op.create_index("ix_cd_release", "classification_decision", ["taxonomy_release_id"])

    # ------------------------------------------------------------------ #
    # classification_decision_candidate_cause  (§10.2)                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "classification_decision_candidate_cause",
        sa.Column(
            "classification_decision_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_decision.classification_decision_id",
                name="fk_cdcc_decision",
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
                name="fk_cdcc_cause",
                ondelete="RESTRICT",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("rank", sa.SmallInteger, nullable=False),
        sa.Column("confidence", sa.Numeric(6, 5), nullable=True),
        sa.Column("rationale_masked", sa.Text, nullable=True),
        sa.Column(
            "source",
            sa.String(32),
            nullable=False,
            comment="e.g. AI, HUMAN",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_cdcc_confidence",
        ),
    )

    op.create_index(
        "ix_cdcc_decision",
        "classification_decision_candidate_cause",
        ["classification_decision_id"],
    )

    # ------------------------------------------------------------------ #
    # classification_decision_prediction_ref  (§10.3)                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "classification_decision_prediction_ref",
        sa.Column(
            "classification_decision_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_decision.classification_decision_id",
                name="fk_cdpr_decision",
                ondelete="CASCADE",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "prediction_event_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "prediction_event.prediction_event_id",
                name="fk_cdpr_prediction",
                ondelete="RESTRICT",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "relation",
            sa.String(32),
            nullable=False,
            comment="ACCEPTED | CORRECTED_FROM | CONSIDERED",
        ),
        sa.CheckConstraint(
            "relation IN ('ACCEPTED','CORRECTED_FROM','CONSIDERED')",
            name="ck_cdpr_relation",
        ),
    )

    # ------------------------------------------------------------------ #
    # review_event  (§10.4)  — immutable semantic review log              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "review_event",
        sa.Column(
            "review_event_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_re_item",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "prediction_run_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "prediction_run.prediction_run_id",
                name="fk_re_prediction_run",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column(
            "classification_decision_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "classification_decision.classification_decision_id",
                name="fk_re_decision",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column(
            "action",
            sa.String(64),
            nullable=False,
            comment=(
                "ACCEPT | CORRECT | MARK_UNKNOWN | MARK_MISSING | "
                "MARK_NOT_APPLICABLE | SPLIT_REQUIRED | SKIP"
            ),
        ),
        sa.Column("reviewer_user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        # Action CHECK
        sa.CheckConstraint(
            "action IN ('ACCEPT','CORRECT','MARK_UNKNOWN','MARK_MISSING',"
            "'MARK_NOT_APPLICABLE','SPLIT_REQUIRED','SKIP')",
            name="ck_re_action",
        ),
    )

    op.create_index("ix_re_item", "review_event", ["feedback_item_id"])
    op.create_index("ix_re_decision", "review_event", ["classification_decision_id"])


def downgrade() -> None:
    op.drop_index("ix_re_decision", table_name="review_event")
    op.drop_index("ix_re_item", table_name="review_event")
    op.drop_table("review_event")

    op.drop_table("classification_decision_prediction_ref")

    op.drop_index(
        "ix_cdcc_decision", table_name="classification_decision_candidate_cause"
    )
    op.drop_table("classification_decision_candidate_cause")

    op.drop_index("ix_cd_release", table_name="classification_decision")
    op.drop_index("ix_cd_item_version", table_name="classification_decision")
    op.drop_table("classification_decision")
