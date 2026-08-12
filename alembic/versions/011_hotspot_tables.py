"""011 — Hotspot Tables.

Creates:
  - hotspot_rule            (§13.1)
  - hotspot                 (§13.2)
  - feedback_item_hotspot   (§13.3)
  - hotspot_timeline_event  (§13.4)

Revision ID: 011
Revises: 010
Create Date: 2026-08-12
Issue: #3  Branch: feature/m0-003-operational-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: str | None = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # hotspot_rule  (§13.1)                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        "hotspot_rule",
        sa.Column(
            "hotspot_rule_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("rule_version", sa.String(32), nullable=False),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_hr_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("window_minutes", sa.Integer, nullable=False),
        sa.Column("threshold_count", sa.Integer, nullable=False),
        sa.Column("location_level", sa.String(32), nullable=False),
        sa.Column("dimension_config_json", sa.JSON, nullable=False),
        sa.Column("eligibility_definition_version", sa.String(32), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_hr_project", "hotspot_rule", ["project_id"])

    # ------------------------------------------------------------------ #
    # hotspot  (§13.2)                                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "hotspot",
        sa.Column(
            "hotspot_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "hotspot_rule_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "hotspot_rule.hotspot_rule_id",
                name="fk_hotspot_rule",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_hotspot_release",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "dimension_key",
            sa.String(512),
            nullable=False,
            comment="Deterministic composite key for idempotency",
        ),
        sa.Column(
            "service_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service.service_id",
                name="fk_hotspot_service",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "issue_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "issue.issue_id",
                name="fk_hotspot_issue",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "location.location_id",
                name="fk_hotspot_location",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
        sa.Column("window_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("window_end", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("evidence_count", sa.Integer, nullable=False),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default="CANDIDATE",
            comment="hotspot_status enum value",
        ),
        sa.Column("operational_severity", sa.String(8), nullable=False),
        sa.Column("assigned_user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_team_key", sa.String(128), nullable=True),
        sa.Column("first_seen_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("resolution_summary", sa.Text, nullable=True),
        sa.Column(
            "version",
            sa.Integer,
            nullable=False,
            server_default=sa.text("1"),
            comment="Optimistic concurrency version",
        ),
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
        # Idempotency key (§13.2)
        sa.UniqueConstraint(
            "hotspot_rule_id",
            "dimension_key",
            "window_start",
            "window_end",
            name="uq_hotspot_idempotency",
        ),
        sa.CheckConstraint(
            "status IN ('CANDIDATE','ACKNOWLEDGED','INVESTIGATING','RESOLVED','DISMISSED','REOPENED')",
            name="ck_hotspot_status",
        ),
        sa.CheckConstraint(
            "operational_severity IN ('SEV-1','SEV-2','SEV-3','SEV-4')",
            name="ck_hotspot_severity",
        ),
    )

    op.create_index(
        "ix_hotspot_project_status",
        "hotspot",
        ["project_id", "status", sa.text("last_seen_at DESC")],
    )
    op.create_index(
        "ix_hotspot_rule_dim", "hotspot", ["hotspot_rule_id", "dimension_key"]
    )

    # ------------------------------------------------------------------ #
    # feedback_item_hotspot  (§13.3)                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "feedback_item_hotspot",
        sa.Column(
            "hotspot_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "hotspot.hotspot_id",
                name="fk_fih_hotspot",
                ondelete="CASCADE",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "feedback_item_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "feedback_item.feedback_item_id",
                name="fk_fih_item",
                ondelete="RESTRICT",
            ),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "linked_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "evidence_role",
            sa.String(32),
            nullable=False,
            comment="e.g. PRIMARY, SUPPORTING",
        ),
    )

    op.create_index(
        "ix_fih_hotspot_item",
        "feedback_item_hotspot",
        ["hotspot_id", "feedback_item_id"],
    )
    op.create_index("ix_fih_item", "feedback_item_hotspot", ["feedback_item_id"])

    # ------------------------------------------------------------------ #
    # hotspot_timeline_event  (§13.4)  — append-only                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "hotspot_timeline_event",
        sa.Column(
            "hotspot_timeline_event_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "hotspot_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "hotspot.hotspot_id",
                name="fk_hte_hotspot",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("from_status", sa.String(32), nullable=True),
        sa.Column("to_status", sa.String(32), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("correlation_id", sa.String(128), nullable=False),
    )

    op.create_index("ix_hte_hotspot", "hotspot_timeline_event", ["hotspot_id"])


def downgrade() -> None:
    op.drop_index("ix_hte_hotspot", table_name="hotspot_timeline_event")
    op.drop_table("hotspot_timeline_event")

    op.drop_index("ix_fih_item", table_name="feedback_item_hotspot")
    op.drop_index("ix_fih_hotspot_item", table_name="feedback_item_hotspot")
    op.drop_table("feedback_item_hotspot")

    op.drop_index("ix_hotspot_rule_dim", table_name="hotspot")
    op.drop_index("ix_hotspot_project_status", table_name="hotspot")
    op.drop_table("hotspot")

    op.drop_index("ix_hr_project", table_name="hotspot_rule")
    op.drop_table("hotspot_rule")
