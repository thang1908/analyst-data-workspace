"""015 — Additional Indexes and Constraints.

Adds all remaining indexes from §18 Index Strategy that were not created
inline with the table DDL, plus any cross-table CHECK triggers or
additional performance indexes revealed by pilot query analysis.

Revision ID: 015
Revises: 014
Create Date: 2026-08-12
Issue: #4  Branch: feature/m0-004-views-indexes-seed
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "015"
down_revision: str | None = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # feedback  (§18)                                                     #
    # ------------------------------------------------------------------ #
    # (project_id, reported_at DESC) — already in 007
    # (source_system, source_record_key) — already in 007
    # (raw_content_checksum) — already in 007
    # Add: index to quickly find feedbacks for a given import job
    op.create_index(
        "ix_feedback_import_job",
        "feedback",
        ["import_job_id"],
    )

    # ------------------------------------------------------------------ #
    # feedback_item  (§18)                                                #
    # ------------------------------------------------------------------ #
    # (feedback_id) — already in 007
    # (location_id) — already in 007
    # (status, analytic_eligibility) — already in 007
    # Add: composite for analytics view fast path
    op.create_index(
        "ix_fi_analytics_path",
        "feedback_item",
        ["status", "analytic_eligibility", "feedback_id"],
    )

    # ------------------------------------------------------------------ #
    # classification_current  (§18)                                       #
    # ------------------------------------------------------------------ #
    # (primary_service_id, issue_id) — already in 010
    # (customer_lifecycle_step_id) — already in 010
    # (service_request_step_id) — already in 010
    # (sentiment) — already in 010
    # (operational_severity) — already in 010
    # (last_decision_at) — already in 010
    # Add: stage-level drill-down
    op.create_index(
        "ix_cc_stage",
        "classification_current",
        ["customer_lifecycle_stage_id"],
    )

    # ------------------------------------------------------------------ #
    # prediction_event  (§18)                                             #
    # ------------------------------------------------------------------ #
    # (feedback_item_id, field_name, created_at) — already in 008

    # ------------------------------------------------------------------ #
    # classification_decision  (§18)                                      #
    # ------------------------------------------------------------------ #
    # (feedback_item_id, decision_version DESC) — already in 009
    # Add: index by decided_at for timeline queries
    op.create_index(
        "ix_cd_decided_at",
        "classification_decision",
        [sa.text("decided_at DESC")],
    )

    # ------------------------------------------------------------------ #
    # hotspot  (§18)                                                      #
    # ------------------------------------------------------------------ #
    # (project_id, status, last_seen_at DESC) — already in 011
    # (hotspot_rule_id, dimension_key) — already in 011
    # Add: service+issue dimension for hotspot analytics
    op.create_index(
        "ix_hotspot_service_issue",
        "hotspot",
        ["service_id", "issue_id"],
    )

    # ------------------------------------------------------------------ #
    # feedback_item_hotspot  (§18)                                        #
    # ------------------------------------------------------------------ #
    # (hotspot_id, feedback_item_id) — already in 011
    # (feedback_item_id) — already in 011

    # ------------------------------------------------------------------ #
    # import_job  (§18)                                                   #
    # ------------------------------------------------------------------ #
    # (project_id, created_at DESC) — already in 006
    # (status, created_at) — already in 006
    # Add: correlation_id index for tracing
    op.create_index(
        "ix_import_job_correlation",
        "import_job",
        ["correlation_id"],
    )

    # ------------------------------------------------------------------ #
    # audit_event  (§18)                                                  #
    # ------------------------------------------------------------------ #
    # (resource_type, resource_id, occurred_at DESC) — already in 012
    # (actor_user_id, occurred_at DESC) — already in 012
    # Add: correlation_id for distributed tracing
    op.create_index(
        "ix_audit_correlation",
        "audit_event",
        ["correlation_id"],
    )

    # ------------------------------------------------------------------ #
    # Additional: affected_channel for drill-down (§17.1)                 #
    # ------------------------------------------------------------------ #
    op.create_index(
        "ix_fiac_channel",
        "feedback_item_affected_channel",
        ["interaction_channel_id"],
    )

    # ------------------------------------------------------------------ #
    # Additional: hotspot_timeline_event ordering                         #
    # ------------------------------------------------------------------ #
    op.create_index(
        "ix_hte_hotspot_created",
        "hotspot_timeline_event",
        ["hotspot_id", sa.text("created_at ASC")],
    )

    # ------------------------------------------------------------------ #
    # Additional: review_event ordering                                   #
    # ------------------------------------------------------------------ #
    op.create_index(
        "ix_re_item_created",
        "review_event",
        ["feedback_item_id", sa.text("created_at DESC")],
    )

    # ------------------------------------------------------------------ #
    # Additional: pilot_scope_manifest active lookup                      #
    # ------------------------------------------------------------------ #
    op.create_index(
        "ix_psm_user_active",
        "pilot_scope_manifest",
        ["user_id", "active"],
    )


def downgrade() -> None:
    op.drop_index("ix_psm_user_active", table_name="pilot_scope_manifest")
    op.drop_index("ix_re_item_created", table_name="review_event")
    op.drop_index("ix_hte_hotspot_created", table_name="hotspot_timeline_event")
    op.drop_index("ix_fiac_channel", table_name="feedback_item_affected_channel")
    op.drop_index("ix_audit_correlation", table_name="audit_event")
    op.drop_index("ix_import_job_correlation", table_name="import_job")
    op.drop_index("ix_hotspot_service_issue", table_name="hotspot")
    op.drop_index("ix_cd_decided_at", table_name="classification_decision")
    op.drop_index("ix_cc_stage", table_name="classification_current")
    op.drop_index("ix_fi_analytics_path", table_name="feedback_item")
    op.drop_index("ix_feedback_import_job", table_name="feedback")
