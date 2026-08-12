"""012 — Audit and Security Tables.

Creates:
  - audit_event           (§15.1)  — append-only semantic audit log
  - pilot_scope_manifest  (§15.2)  — P0 project-level access scope

Revision ID: 012
Revises: 011
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "012"
down_revision: str | None = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # audit_event  (§15.1)  — append-only                                #
    # ------------------------------------------------------------------ #
    op.create_table(
        "audit_event",
        sa.Column(
            "audit_event_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "occurred_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("actor_user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_role", sa.String(64), nullable=False),
        sa.Column(
            "action",
            sa.String(128),
            nullable=False,
            comment=(
                "e.g. taxonomy.publish, import.execute, feedback_item.split, "
                "classification.decision, hotspot.assign"
            ),
        ),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column(
            "resource_id",
            sa.String(255),
            nullable=True,
            comment="UUID or stable code of the affected resource",
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "before_ref",
            sa.JSON,
            nullable=True,
            comment="Non-PII reference snapshot before change",
        ),
        sa.Column(
            "after_ref",
            sa.JSON,
            nullable=True,
            comment="Non-PII reference snapshot after change",
        ),
        sa.Column("metadata_json", sa.JSON, nullable=True),
    )

    op.create_index(
        "ix_audit_resource",
        "audit_event",
        ["resource_type", "resource_id", sa.text("occurred_at DESC")],
    )
    op.create_index(
        "ix_audit_actor",
        "audit_event",
        ["actor_user_id", sa.text("occurred_at DESC")],
    )
    op.create_index("ix_audit_project", "audit_event", ["project_id", "occurred_at"])

    # ------------------------------------------------------------------ #
    # pilot_scope_manifest  (§15.2)                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "pilot_scope_manifest",
        sa.Column(
            "pilot_scope_manifest_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role_key",
            sa.String(64),
            nullable=False,
            comment="e.g. PILOT_ADMIN, ANALYST, REVIEWER, VIEWER",
        ),
        sa.Column(
            "raw_pii_allowed",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
            comment="Grants access to content_raw field and raw exports",
        ),
        sa.Column(
            "export_allowed",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("effective_from", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("effective_to", sa.TIMESTAMP(timezone=True), nullable=True),
        # One active record per user+project
        sa.UniqueConstraint(
            "user_id", "project_id", name="uq_psm_user_project"
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_psm_effective_dates",
        ),
    )

    op.create_index(
        "ix_psm_user_project", "pilot_scope_manifest", ["user_id", "project_id"]
    )
    op.create_index("ix_psm_project", "pilot_scope_manifest", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_psm_project", table_name="pilot_scope_manifest")
    op.drop_index("ix_psm_user_project", table_name="pilot_scope_manifest")
    op.drop_table("pilot_scope_manifest")

    op.drop_index("ix_audit_project", table_name="audit_event")
    op.drop_index("ix_audit_actor", table_name="audit_event")
    op.drop_index("ix_audit_resource", table_name="audit_event")
    op.drop_table("audit_event")
