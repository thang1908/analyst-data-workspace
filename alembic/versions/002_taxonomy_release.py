"""002 — Taxonomy release table.

Creates the `taxonomy_release` table which is the immutable version
boundary for published taxonomy/reference classification semantics (§6.1).

Revision ID: 002
Revises: 001
Create Date: 2026-08-12
Issue: #2  Branch: feature/m0-002-taxonomy-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # taxonomy_release  (§6.1)                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "taxonomy_release",
        # Primary key
        sa.Column(
            "taxonomy_release_id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Internal identity (UUID PK)",
        ),
        # Version
        sa.Column(
            "version",
            sa.String(32),
            nullable=False,
            comment="Unique semantic version e.g. 3.0.0",
        ),
        # Status — reuse the enum type created in migration 001 via raw DDL
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default="DRAFT",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'APPROVED', 'PUBLISHED', 'RETIRED')",
            name="ck_taxonomy_release_status",
        ),
        # Effective dates
        sa.Column("effective_from", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("effective_to", sa.TIMESTAMP(timezone=True), nullable=True),
        # Source integrity
        sa.Column(
            "source_checksum",
            sa.String(128),
            nullable=False,
            comment="SHA-256 / checksum of structured seed input",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        # Approval metadata
        sa.Column("approved_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Publication metadata
        sa.Column("published_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Audit
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=False),
        # ---------------------------------------------------------------- #
        # Constraints                                                       #
        # ---------------------------------------------------------------- #
        sa.UniqueConstraint("version", name="uq_taxonomy_release_version"),
        # effective_to IS NULL OR effective_to > effective_from
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_taxonomy_release_effective_dates",
        ),
        # PUBLISHED → published_by / published_at / effective_from NOT NULL
        sa.CheckConstraint(
            """
            status != 'PUBLISHED'
            OR (
                published_by IS NOT NULL
                AND published_at IS NOT NULL
                AND effective_from IS NOT NULL
            )
            """,
            name="ck_taxonomy_release_published_fields",
        ),
        # APPROVED → approved_by / approved_at NOT NULL
        sa.CheckConstraint(
            """
            status NOT IN ('APPROVED', 'PUBLISHED', 'RETIRED')
            OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)
            """,
            name="ck_taxonomy_release_approved_fields",
        ),
    )


def downgrade() -> None:
    op.drop_table("taxonomy_release")
