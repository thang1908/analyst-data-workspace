"""005 — Channel, Location and Service Owner Config tables.

Creates:
  - interaction_channel   (§6.10)
  - location              (§6.11)
  - service_owner_config  (§6.12)

Revision ID: 005
Revises: 004
Create Date: 2026-08-12
Issue: #2  Branch: feature/m0-002-taxonomy-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels = None
depends_on = None

FK_RESTRICT = "RESTRICT"


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # interaction_channel  (§6.10)                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "interaction_channel",
        sa.Column(
            "interaction_channel_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "channel_code",
            sa.String(32),
            nullable=False,
            comment=(
                "Canonical codes: CH-APP, CH-WEB, CH-HOTLINE, CH-EMAIL, "
                "CH-FRONTDESK, CH-SOCIAL, CH-INPERSON, CH-SYSTEM"
            ),
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint("channel_code", name="uq_interaction_channel_code"),
    )

    # ------------------------------------------------------------------ #
    # location  (§6.11)                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "location",
        sa.Column(
            "location_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "parent_location_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "location.location_id",
                name="fk_location_parent",
                ondelete=FK_RESTRICT,
            ),
            nullable=True,
            comment="Self-referential for hierarchy: PROJECT > BUILDING > FLOOR > UNIT/ZONE/ASSET_AREA",
        ),
        sa.Column(
            "location_code",
            sa.String(64),
            nullable=False,
        ),
        sa.Column(
            "location_type",
            sa.String(32),
            nullable=False,
            comment="e.g. PROJECT, BUILDING, FLOOR, UNIT, ZONE, ASSET_AREA",
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("path_code", sa.Text, nullable=True, comment="Materialized path for fast hierarchy queries"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "metadata_json",
            sa.JSON,
            nullable=True,
        ),
        # Unique code per project
        sa.UniqueConstraint("project_id", "location_code", name="uq_location_project_code"),
    )

    op.create_index("ix_location_project", "location", ["project_id"])
    op.create_index("ix_location_parent", "location", ["parent_location_id"])
    # For hierarchy traversal via path_code prefix search
    op.create_index("ix_location_path_code", "location", ["path_code"])

    # ------------------------------------------------------------------ #
    # service_owner_config  (§6.12)                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "service_owner_config",
        sa.Column(
            "service_owner_config_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "service_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service.service_id",
                name="fk_soc_service",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "location_scope_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "location.location_id",
                name="fk_soc_location_scope",
                ondelete=FK_RESTRICT,
            ),
            nullable=True,
            comment="Optional: limit ownership to a specific location subtree",
        ),
        sa.Column(
            "owner_user_id",
            sa.UUID(as_uuid=True),
            nullable=True,
            comment="Auth user UUID — resolved outside this DB schema",
        ),
        sa.Column(
            "owner_team_key",
            sa.String(128),
            nullable=True,
            comment="Team identifier string (alternative to owner_user_id)",
        ),
        sa.Column(
            "effective_from",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column("effective_to", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # At least one of owner_user_id or owner_team_key must be set
        sa.CheckConstraint(
            "owner_user_id IS NOT NULL OR owner_team_key IS NOT NULL",
            name="ck_soc_owner_not_both_null",
        ),
    )

    op.create_index("ix_soc_project_service", "service_owner_config", ["project_id", "service_id"])
    op.create_index("ix_soc_location_scope", "service_owner_config", ["location_scope_id"])


def downgrade() -> None:
    op.drop_index("ix_soc_location_scope", table_name="service_owner_config")
    op.drop_index("ix_soc_project_service", table_name="service_owner_config")
    op.drop_table("service_owner_config")

    op.drop_index("ix_location_path_code", table_name="location")
    op.drop_index("ix_location_parent", table_name="location")
    op.drop_index("ix_location_project", table_name="location")
    op.drop_table("location")

    op.drop_table("interaction_channel")
