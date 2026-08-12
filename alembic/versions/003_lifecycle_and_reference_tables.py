"""003 — Lifecycle and reference tables.

Creates:
  - customer_lifecycle_stage  (§6.2)
  - customer_lifecycle_step   (§6.3)
  - service_request_step      (§6.4)

All tables reference taxonomy_release_id from the parent release.

Revision ID: 003
Revises: 002
Create Date: 2026-08-12
Issue: #2  Branch: feature/m0-002-taxonomy-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels = None
depends_on = None

# Shared FK options
FK_ON_DELETE = "RESTRICT"


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # customer_lifecycle_stage  (§6.2)                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "customer_lifecycle_stage",
        sa.Column(
            "customer_lifecycle_stage_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_cls_taxonomy_release",
                ondelete=FK_ON_DELETE,
            ),
            nullable=False,
        ),
        sa.Column(
            "stage_code",
            sa.String(16),
            nullable=False,
            comment="e.g. A, C, TR, HO, RES, OPS",
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("definition", sa.Text, nullable=True),
        sa.Column("sort_order", sa.SmallInteger, nullable=False),
        sa.Column(
            "active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "stage_code",
            name="uq_cls_release_stage_code",
        ),
    )

    # Index for FK lookups
    op.create_index(
        "ix_customer_lifecycle_stage_release",
        "customer_lifecycle_stage",
        ["taxonomy_release_id"],
    )

    # ------------------------------------------------------------------ #
    # customer_lifecycle_step  (§6.3)                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "customer_lifecycle_step",
        sa.Column(
            "customer_lifecycle_step_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_clst_taxonomy_release",
                ondelete=FK_ON_DELETE,
            ),
            nullable=False,
        ),
        sa.Column(
            "customer_lifecycle_stage_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "customer_lifecycle_stage.customer_lifecycle_stage_id",
                name="fk_clst_stage",
                ondelete=FK_ON_DELETE,
            ),
            nullable=False,
            comment="Must belong to the same taxonomy_release_id",
        ),
        sa.Column(
            "step_code",
            sa.String(20),
            nullable=False,
            comment="e.g. RES-03",
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("definition", sa.Text, nullable=True),
        sa.Column("sort_order", sa.SmallInteger, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "step_code",
            name="uq_clst_release_step_code",
        ),
    )

    op.create_index(
        "ix_customer_lifecycle_step_release",
        "customer_lifecycle_step",
        ["taxonomy_release_id"],
    )
    op.create_index(
        "ix_customer_lifecycle_step_stage",
        "customer_lifecycle_step",
        ["customer_lifecycle_stage_id"],
    )

    # ------------------------------------------------------------------ #
    # service_request_step  (§6.4)                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "service_request_step",
        sa.Column(
            "service_request_step_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "taxonomy_release.taxonomy_release_id",
                name="fk_srs_taxonomy_release",
                ondelete=FK_ON_DELETE,
            ),
            nullable=False,
        ),
        sa.Column(
            "step_code",
            sa.String(20),
            nullable=False,
            comment="e.g. SRV-01 .. SRV-08",
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("definition", sa.Text, nullable=True),
        sa.Column("sort_order", sa.SmallInteger, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "step_code",
            name="uq_srs_release_step_code",
        ),
    )

    op.create_index(
        "ix_service_request_step_release",
        "service_request_step",
        ["taxonomy_release_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_service_request_step_release", table_name="service_request_step")
    op.drop_table("service_request_step")

    op.drop_index("ix_customer_lifecycle_step_stage", table_name="customer_lifecycle_step")
    op.drop_index("ix_customer_lifecycle_step_release", table_name="customer_lifecycle_step")
    op.drop_table("customer_lifecycle_step")

    op.drop_index("ix_customer_lifecycle_stage_release", table_name="customer_lifecycle_stage")
    op.drop_table("customer_lifecycle_stage")
