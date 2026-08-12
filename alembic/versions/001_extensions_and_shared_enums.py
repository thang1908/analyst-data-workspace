"""001 — Extensions and shared enums.

Enable pgcrypto/uuid-ossp, create all canonical PostgreSQL enum types
used across the platform.

Revision ID: 001
Revises: (initial)
Create Date: 2026-08-12
Issue: #2  Branch: feature/m0-002-taxonomy-migrations
"""

from __future__ import annotations

from alembic import op

# revision identifiers
revision: str = "001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # Extensions                                                           #
    # ------------------------------------------------------------------ #
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ------------------------------------------------------------------ #
    # Enum: value_status  (§5.1)                                          #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE value_status AS ENUM (
            'KNOWN',
            'UNKNOWN',
            'MISSING',
            'NOT_APPLICABLE'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: taxonomy_release_status  (§5.2)                               #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE taxonomy_release_status AS ENUM (
            'DRAFT',
            'APPROVED',
            'PUBLISHED',
            'RETIRED'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: classification_state  (§5.3)                                  #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE classification_state AS ENUM (
            'PENDING_REVIEW',
            'ACCEPTED',
            'REJECTED',
            'SUPERSEDED'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: decision_source  (§5.4)                                       #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE decision_source AS ENUM (
            'MANUAL',
            'SOURCE_TRUSTED',
            'HUMAN_ACCEPTED_AI',
            'HUMAN_CORRECTED_AI',
            'POLICY_AUTO_APPLIED',
            'SYSTEM_MIGRATION'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: sentiment  (§5.5)                                             #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE sentiment AS ENUM (
            'POSITIVE',
            'NEUTRAL',
            'NEGATIVE',
            'UNKNOWN'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: operational_severity  (§5.6)                                  #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE operational_severity AS ENUM (
            'SEV-1',
            'SEV-2',
            'SEV-3',
            'SEV-4'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: cause_determination_status  (§5.7)                            #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE cause_determination_status AS ENUM (
            'NOT_ASSESSED',
            'UNKNOWN',
            'SUGGESTED',
            'UNDER_INVESTIGATION',
            'CONFIRMED',
            'NOT_APPLICABLE'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: analytic_eligibility  (§5.8)                                  #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE analytic_eligibility AS ENUM (
            'INCLUDED',
            'EXCLUDED',
            'PENDING'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: feedback_item_status  (§5.9)                                  #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE feedback_item_status AS ENUM (
            'ACTIVE',
            'SPLIT_PARENT',
            'RETIRED'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: import_job_status  (§5.10)                                    #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE import_job_status AS ENUM (
            'UPLOADED',
            'MAPPED',
            'VALIDATING',
            'VALIDATED',
            'QUEUED',
            'PROCESSING',
            'COMPLETED',
            'PARTIAL',
            'FAILED',
            'CANCELLING',
            'CANCELLED'
        )
    """)

    # ------------------------------------------------------------------ #
    # Enum: hotspot_status  (§5.11)                                       #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE TYPE hotspot_status AS ENUM (
            'CANDIDATE',
            'ACKNOWLEDGED',
            'INVESTIGATING',
            'RESOLVED',
            'DISMISSED',
            'REOPENED'
        )
    """)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS hotspot_status")
    op.execute("DROP TYPE IF EXISTS import_job_status")
    op.execute("DROP TYPE IF EXISTS feedback_item_status")
    op.execute("DROP TYPE IF EXISTS analytic_eligibility")
    op.execute("DROP TYPE IF EXISTS cause_determination_status")
    op.execute("DROP TYPE IF EXISTS operational_severity")
    op.execute("DROP TYPE IF EXISTS sentiment")
    op.execute("DROP TYPE IF EXISTS decision_source")
    op.execute("DROP TYPE IF EXISTS classification_state")
    op.execute("DROP TYPE IF EXISTS taxonomy_release_status")
    op.execute("DROP TYPE IF EXISTS value_status")
