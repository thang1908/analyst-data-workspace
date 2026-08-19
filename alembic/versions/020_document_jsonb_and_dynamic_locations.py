"""020 — Document JSONB and Dynamic Location Indexes.

Upgrades:
  - Alters feedback.source_metadata_json to JSONB
  - Adds GIN index on feedback.source_metadata_json for fast document queries
  - Adds B-tree indexes on location(name) and location(location_code) for fast resolution

Revision ID: 020
Revises: 019
Create Date: 2026-08-18
"""

from __future__ import annotations

from alembic import op

revision: str = "020"
down_revision: str | None = "019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Alter column type to JSONB
    op.execute(
        "ALTER TABLE feedback ALTER COLUMN source_metadata_json TYPE JSONB USING source_metadata_json::jsonb"
    )

    # 2. Add GIN index for document queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_feedback_source_metadata_gin ON feedback USING gin (source_metadata_json)"
    )

    # 3. Add lookup indexes on location
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_location_name ON location (name)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_location_code ON location (location_code)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_feedback_source_metadata_gin")
    op.execute("DROP INDEX IF EXISTS idx_location_name")
    op.execute("DROP INDEX IF EXISTS idx_location_code")
    op.execute(
        "ALTER TABLE feedback ALTER COLUMN source_metadata_json TYPE JSON USING source_metadata_json::json"
    )
