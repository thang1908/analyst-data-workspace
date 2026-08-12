"""004 — Service, Issue, Cause and mapping tables.

Creates:
  - service             (§6.5)
  - issue               (§6.6)
  - cause               (§6.7)
  - issue_cause_map     (§6.8)
  - lifecycle_service_map (§6.9)

Revision ID: 004
Revises: 003
Create Date: 2026-08-12
Issue: #2  Branch: feature/m0-002-taxonomy-migrations
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels = None
depends_on = None

FK_RESTRICT = "RESTRICT"


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # service  (§6.5)                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "service",
        sa.Column(
            "service_id",
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
                name="fk_service_taxonomy_release",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "service_code",
            sa.String(16),
            nullable=False,
            comment="e.g. SV-01 .. SV-10",
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("outcome_definition", sa.Text, nullable=False),
        sa.Column("in_scope", sa.Text, nullable=True),
        sa.Column("out_of_scope", sa.Text, nullable=True),
        sa.Column(
            "default_severity",
            sa.String(8),
            nullable=True,
            comment="SEV-1..4",
        ),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "service_code",
            name="uq_service_release_code",
        ),
    )

    op.create_index("ix_service_release", "service", ["taxonomy_release_id"])

    # ------------------------------------------------------------------ #
    # issue  (§6.6)                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "issue",
        sa.Column(
            "issue_id",
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
                name="fk_issue_taxonomy_release",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service.service_id",
                name="fk_issue_service",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
            comment="Exactly one service in same release (app-enforced cross-FK)",
        ),
        sa.Column(
            "issue_code",
            sa.String(20),
            nullable=False,
            comment="e.g. IS-07-01",
        ),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("definition", sa.Text, nullable=False),
        sa.Column(
            "inclusion_examples",
            sa.JSON,
            nullable=True,
            comment="JSON string array",
        ),
        sa.Column(
            "exclusion_examples",
            sa.JSON,
            nullable=True,
            comment="JSON string array",
        ),
        sa.Column(
            "safety_critical",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("severity_override", sa.String(8), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "issue_code",
            name="uq_issue_release_code",
        ),
    )

    op.create_index("ix_issue_release", "issue", ["taxonomy_release_id"])
    op.create_index("ix_issue_service", "issue", ["service_id"])

    # ------------------------------------------------------------------ #
    # cause  (§6.7)                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "cause",
        sa.Column(
            "cause_id",
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
                name="fk_cause_taxonomy_release",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column("cause_code", sa.String(32), nullable=False),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("mechanism", sa.Text, nullable=True),
        sa.Column("contributing_factor", sa.Text, nullable=True),
        sa.Column("external_condition", sa.Text, nullable=True),
        sa.Column("responsible_party_hint", sa.Text, nullable=True),
        sa.Column("required_evidence", sa.Text, nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "cause_code",
            name="uq_cause_release_code",
        ),
    )

    op.create_index("ix_cause_release", "cause", ["taxonomy_release_id"])

    # ------------------------------------------------------------------ #
    # issue_cause_map  (§6.8)                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "issue_cause_map",
        sa.Column(
            "issue_cause_map_id",
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
                name="fk_icm_taxonomy_release",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "issue_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "issue.issue_id",
                name="fk_icm_issue",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "cause_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "cause.cause_id",
                name="fk_icm_cause",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column("rank_hint", sa.SmallInteger, nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("effective_from", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("effective_to", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.UniqueConstraint(
            "taxonomy_release_id",
            "issue_id",
            "cause_id",
            name="uq_icm_release_issue_cause",
        ),
    )

    op.create_index("ix_icm_issue", "issue_cause_map", ["issue_id"])
    op.create_index("ix_icm_cause", "issue_cause_map", ["cause_id"])
    op.create_index("ix_icm_release", "issue_cause_map", ["taxonomy_release_id"])

    # ------------------------------------------------------------------ #
    # lifecycle_service_map  (§6.9)                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "lifecycle_service_map",
        sa.Column(
            "lifecycle_service_map_id",
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
                name="fk_lsm_taxonomy_release",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "lifecycle_type",
            sa.String(40),
            nullable=False,
            comment="CUSTOMER_LIFECYCLE or SERVICE_REQUEST_LIFECYCLE",
        ),
        # Generic UUID — points to either customer_lifecycle_step or service_request_step
        # Cannot use a typed FK as both are valid targets (app-enforced)
        sa.Column(
            "lifecycle_step_id",
            sa.UUID(as_uuid=True),
            nullable=False,
            comment="FK resolved by lifecycle_type: customer_lifecycle_step or service_request_step",
        ),
        sa.Column(
            "service_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey(
                "service.service_id",
                name="fk_lsm_service",
                ondelete=FK_RESTRICT,
            ),
            nullable=False,
        ),
        sa.Column(
            "mapping_strength",
            sa.String(20),
            nullable=True,
            comment="e.g. PRIMARY, SECONDARY, OPTIONAL",
        ),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("effective_from", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("effective_to", sa.TIMESTAMP(timezone=True), nullable=True),
        # lifecycle_type CHECK
        sa.CheckConstraint(
            "lifecycle_type IN ('CUSTOMER_LIFECYCLE', 'SERVICE_REQUEST_LIFECYCLE')",
            name="ck_lsm_lifecycle_type",
        ),
    )

    op.create_index("ix_lsm_release", "lifecycle_service_map", ["taxonomy_release_id"])
    op.create_index("ix_lsm_step", "lifecycle_service_map", ["lifecycle_step_id"])
    op.create_index("ix_lsm_service", "lifecycle_service_map", ["service_id"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("ix_lsm_service", table_name="lifecycle_service_map")
    op.drop_index("ix_lsm_step", table_name="lifecycle_service_map")
    op.drop_index("ix_lsm_release", table_name="lifecycle_service_map")
    op.drop_table("lifecycle_service_map")

    op.drop_index("ix_icm_release", table_name="issue_cause_map")
    op.drop_index("ix_icm_cause", table_name="issue_cause_map")
    op.drop_index("ix_icm_issue", table_name="issue_cause_map")
    op.drop_table("issue_cause_map")

    op.drop_index("ix_cause_release", table_name="cause")
    op.drop_table("cause")

    op.drop_index("ix_issue_service", table_name="issue")
    op.drop_index("ix_issue_release", table_name="issue")
    op.drop_table("issue")

    op.drop_index("ix_service_release", table_name="service")
    op.drop_table("service")
