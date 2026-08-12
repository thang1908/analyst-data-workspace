"""014 — Analytics Semantic View.

Creates the governed analytics view `analytics_feedback_item_v1` (§17.1)
joining feedback_item, feedback, classification_current and all taxonomy
dimension tables.

Central eligibility predicate (must match across ALL KPIs, charts, exports):
    feedback_item.status = 'ACTIVE'
    AND feedback_item.analytic_eligibility = 'INCLUDED'
    AND classification_current.current_decision_id IS NOT NULL
    AND classification_current.classification_state = 'ACCEPTED'

Revision ID: 014
Revises: 013
Create Date: 2026-08-12
Issue: #4  Branch: feature/m0-004-views-indexes-seed
"""

from __future__ import annotations

from alembic import op

revision: str = "014"
down_revision: str | None = "013"
branch_labels = None
depends_on = None


_VIEW_SQL = """
CREATE OR REPLACE VIEW analytics_feedback_item_v1 AS
SELECT
    -- Feedback Item identifiers
    fi.feedback_item_id,
    fi.feedback_id,
    f.project_id,
    f.reported_at,
    f.source_system,
    f.intake_channel_id,
    fi.location_id,
    loc.location_code,
    loc.location_type,
    loc.name            AS location_name,

    -- Taxonomy release
    cc.taxonomy_release_id,

    -- Customer Lifecycle
    cc.customer_lifecycle_value_status,
    cc.customer_lifecycle_stage_id,
    cls.stage_code      AS customer_lifecycle_stage_code,
    cls.name_vi         AS customer_lifecycle_stage_name_vi,
    cc.customer_lifecycle_step_id,
    clst.step_code      AS customer_lifecycle_step_code,
    clst.name_vi        AS customer_lifecycle_step_name_vi,

    -- Service Request Lifecycle
    cc.service_request_value_status,
    cc.service_request_step_id,
    srs.step_code       AS service_request_step_code,
    srs.name_vi         AS service_request_step_name_vi,

    -- Primary Service
    cc.primary_service_value_status,
    cc.primary_service_id,
    svc.service_code,
    svc.name_vi         AS service_name_vi,
    svc.name_en         AS service_name_en,
    svc.default_severity AS service_default_severity,

    -- Issue
    cc.issue_value_status,
    cc.issue_id,
    iss.issue_code,
    iss.name_vi         AS issue_name_vi,
    iss.name_en         AS issue_name_en,
    iss.safety_critical,

    -- Classification scalars
    cc.sentiment,
    cc.operational_severity,
    cc.cause_determination_status,
    cc.other_reason,
    cc.classification_state,

    -- Decision metadata
    cc.current_decision_id,
    cc.current_decision_version,
    cc.last_decision_at,
    cc.projection_version

FROM feedback_item fi

INNER JOIN feedback f
    ON f.feedback_id = fi.feedback_id

INNER JOIN classification_current cc
    ON cc.feedback_item_id = fi.feedback_item_id

-- Taxonomy dimensions (all LEFT JOIN to preserve rows even when NOT_APPLICABLE)
LEFT JOIN customer_lifecycle_stage cls
    ON cls.customer_lifecycle_stage_id = cc.customer_lifecycle_stage_id

LEFT JOIN customer_lifecycle_step clst
    ON clst.customer_lifecycle_step_id = cc.customer_lifecycle_step_id

LEFT JOIN service_request_step srs
    ON srs.service_request_step_id = cc.service_request_step_id

LEFT JOIN service svc
    ON svc.service_id = cc.primary_service_id

LEFT JOIN issue iss
    ON iss.issue_id = cc.issue_id

LEFT JOIN location loc
    ON loc.location_id = fi.location_id

-- Central eligibility predicate (§17.1)
WHERE fi.status = 'ACTIVE'
  AND fi.analytic_eligibility = 'INCLUDED'
  AND cc.current_decision_id IS NOT NULL
  AND cc.classification_state = 'ACCEPTED';
"""

_DROP_VIEW_SQL = "DROP VIEW IF EXISTS analytics_feedback_item_v1;"


def upgrade() -> None:
    op.execute(_VIEW_SQL)


def downgrade() -> None:
    op.execute(_DROP_VIEW_SQL)
