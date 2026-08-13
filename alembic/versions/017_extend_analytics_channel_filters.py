"""017 — Extend analytics semantic view with P0 channel dimensions.

Adds the fields required by the shared P0 analytics filter and breakdown
contract: canonical intake-channel code and the zero-to-many affected-channel
codes for each feedback item.  The view remains one row per feedback item;
affected channels are represented as a PostgreSQL array so item-volume metrics
continue to use a stable feedback-item grain.

Revision ID: 017
Revises: 016
Create Date: 2026-08-13
Issue: #25
"""

from __future__ import annotations

from alembic import op

revision: str = "017"
down_revision: str | None = "016"
branch_labels = None
depends_on = None


_VIEW_SQL = """
CREATE OR REPLACE VIEW analytics_feedback_item_v1 AS
SELECT
    fi.feedback_item_id,
    fi.feedback_id,
    f.project_id,
    f.reported_at,
    f.source_system,
    f.intake_channel_id,
    fi.location_id,
    loc.location_code,
    loc.location_type,
    loc.name AS location_name,

    cc.taxonomy_release_id,

    cc.customer_lifecycle_value_status,
    cc.customer_lifecycle_stage_id,
    cls.stage_code AS customer_lifecycle_stage_code,
    cls.name_vi AS customer_lifecycle_stage_name_vi,
    cc.customer_lifecycle_step_id,
    clst.step_code AS customer_lifecycle_step_code,
    clst.name_vi AS customer_lifecycle_step_name_vi,

    cc.service_request_value_status,
    cc.service_request_step_id,
    srs.step_code AS service_request_step_code,
    srs.name_vi AS service_request_step_name_vi,

    cc.primary_service_value_status,
    cc.primary_service_id,
    svc.service_code,
    svc.name_vi AS service_name_vi,
    svc.name_en AS service_name_en,
    svc.default_severity AS service_default_severity,

    cc.issue_value_status,
    cc.issue_id,
    iss.issue_code,
    iss.name_vi AS issue_name_vi,
    iss.name_en AS issue_name_en,
    iss.safety_critical,

    cc.sentiment,
    cc.operational_severity,
    cc.cause_determination_status,
    cc.other_reason,
    cc.classification_state,

    cc.current_decision_id,
    cc.current_decision_version,
    cc.last_decision_at,
    cc.projection_version,

    -- Appended columns preserve the existing v1 view contract.
    intake_channel.channel_code AS intake_channel_code,
    loc.path_code AS location_path_code,
    COALESCE(affected_channels.affected_channel_codes, ARRAY[]::varchar[])
        AS affected_channel_codes
FROM feedback_item fi
INNER JOIN feedback f
    ON f.feedback_id = fi.feedback_id
INNER JOIN classification_current cc
    ON cc.feedback_item_id = fi.feedback_item_id
LEFT JOIN interaction_channel intake_channel
    ON intake_channel.interaction_channel_id = f.intake_channel_id
LEFT JOIN location loc
    ON loc.location_id = fi.location_id
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(DISTINCT affected_channel.channel_code ORDER BY affected_channel.channel_code)
        AS affected_channel_codes
    FROM feedback_item_affected_channel fiac
    INNER JOIN interaction_channel affected_channel
        ON affected_channel.interaction_channel_id = fiac.interaction_channel_id
    WHERE fiac.feedback_item_id = fi.feedback_item_id
) affected_channels ON TRUE
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
WHERE fi.status = 'ACTIVE'
  AND fi.analytic_eligibility = 'INCLUDED'
  AND cc.current_decision_id IS NOT NULL
  AND cc.classification_state = 'ACCEPTED';
"""


def upgrade() -> None:
    op.execute(_VIEW_SQL)


def downgrade() -> None:
    op.execute("DROP VIEW analytics_feedback_item_v1")
    op.execute("""
    CREATE OR REPLACE VIEW analytics_feedback_item_v1 AS
    SELECT
        fi.feedback_item_id, fi.feedback_id, f.project_id, f.reported_at,
        f.source_system, f.intake_channel_id, fi.location_id, loc.location_code,
        loc.location_type, loc.name AS location_name, cc.taxonomy_release_id,
        cc.customer_lifecycle_value_status, cc.customer_lifecycle_stage_id,
        cls.stage_code AS customer_lifecycle_stage_code,
        cls.name_vi AS customer_lifecycle_stage_name_vi,
        cc.customer_lifecycle_step_id,
        clst.step_code AS customer_lifecycle_step_code,
        clst.name_vi AS customer_lifecycle_step_name_vi,
        cc.service_request_value_status, cc.service_request_step_id,
        srs.step_code AS service_request_step_code,
        srs.name_vi AS service_request_step_name_vi,
        cc.primary_service_value_status, cc.primary_service_id, svc.service_code,
        svc.name_vi AS service_name_vi, svc.name_en AS service_name_en,
        svc.default_severity AS service_default_severity,
        cc.issue_value_status, cc.issue_id, iss.issue_code,
        iss.name_vi AS issue_name_vi, iss.name_en AS issue_name_en,
        iss.safety_critical, cc.sentiment, cc.operational_severity,
        cc.cause_determination_status, cc.other_reason, cc.classification_state,
        cc.current_decision_id, cc.current_decision_version, cc.last_decision_at,
        cc.projection_version
    FROM feedback_item fi
    INNER JOIN feedback f ON f.feedback_id = fi.feedback_id
    INNER JOIN classification_current cc ON cc.feedback_item_id = fi.feedback_item_id
    LEFT JOIN customer_lifecycle_stage cls
        ON cls.customer_lifecycle_stage_id = cc.customer_lifecycle_stage_id
    LEFT JOIN customer_lifecycle_step clst
        ON clst.customer_lifecycle_step_id = cc.customer_lifecycle_step_id
    LEFT JOIN service_request_step srs
        ON srs.service_request_step_id = cc.service_request_step_id
    LEFT JOIN service svc ON svc.service_id = cc.primary_service_id
    LEFT JOIN issue iss ON iss.issue_id = cc.issue_id
    LEFT JOIN location loc ON loc.location_id = fi.location_id
    WHERE fi.status = 'ACTIVE'
      AND fi.analytic_eligibility = 'INCLUDED'
      AND cc.current_decision_id IS NOT NULL
      AND cc.classification_state = 'ACCEPTED';
    """)
