"""Parameterized PostgreSQL queries over the governed analytics semantic view."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

ANALYTICS_VIEW: Final = "analytics_feedback_item_v1"

# These expressions are source controlled SQL fragments, never user-provided.
@dataclass(frozen=True, slots=True)
class BreakdownDimensionDefinition:
    code_expression: str
    name_expression: str


BREAKDOWN_DIMENSIONS: Final[Mapping[str, BreakdownDimensionDefinition]] = MappingProxyType(
    {
        "service": BreakdownDimensionDefinition("item.service_code", "item.service_name_vi"),
        "issue": BreakdownDimensionDefinition("item.issue_code", "item.issue_name_vi"),
        "journey_stage": BreakdownDimensionDefinition(
            "item.customer_lifecycle_stage_code", "item.customer_lifecycle_stage_name_vi"
        ),
        "journey_step": BreakdownDimensionDefinition(
            "item.customer_lifecycle_step_code", "item.customer_lifecycle_step_name_vi"
        ),
        "service_request_step": BreakdownDimensionDefinition(
            "item.service_request_step_code", "item.service_request_step_name_vi"
        ),
        "location": BreakdownDimensionDefinition("item.location_code", "item.location_name"),
        "intake_channel": BreakdownDimensionDefinition("item.intake_channel_code", "intake_channel.name_vi"),
        "sentiment": BreakdownDimensionDefinition(
            "item.sentiment",
            "CASE item.sentiment "
            "WHEN 'POSITIVE' THEN 'Tích cực' WHEN 'NEGATIVE' THEN 'Tiêu cực' "
            "WHEN 'NEUTRAL' THEN 'Trung tính' ELSE 'Chưa xác định' END",
        ),
        "severity": BreakdownDimensionDefinition(
            "item.operational_severity",
            "CASE item.operational_severity "
            "WHEN 'SEV-1' THEN 'Nghiêm trọng' WHEN 'SEV-2' THEN 'Cao' "
            "WHEN 'SEV-3' THEN 'Trung bình' WHEN 'SEV-4' THEN 'Thấp' "
            "ELSE 'Chưa xác định' END",
        ),
        # Compatibility with the task wording; API clients should use
        # ``journey_stage``.
        "stage": BreakdownDimensionDefinition(
            "item.customer_lifecycle_stage_code", "item.customer_lifecycle_stage_name_vi"
        ),
    }
)

AFFECTED_CHANNEL_BREAKDOWN_SQL: Final = f"""
SELECT
    COALESCE(affected_channel.channel_code, 'UNKNOWN') AS dimension_key,
    COALESCE(affected_channel_taxonomy.name_vi, 'Chưa xác định') AS dimension_name,
    COUNT(DISTINCT item.feedback_item_id) AS count,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'NEGATIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(COUNT(DISTINCT CASE WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE') THEN item.feedback_item_id END), 0),
        0.0
    ) AS negative_rate,
    COUNT(DISTINCT CASE WHEN hotspot.status NOT IN ('RESOLVED', 'DISMISSED') THEN hotspot.hotspot_id END)
        AS active_hotspots,
    COALESCE(
        COUNT(DISTINCT item.feedback_item_id)::double precision
        / NULLIF(SUM(COUNT(DISTINCT item.feedback_item_id)) OVER (), 0),
        0.0
    ) AS percentage
FROM {ANALYTICS_VIEW} AS item
LEFT JOIN LATERAL UNNEST(item.affected_channel_codes)
    AS affected_channel(channel_code) ON TRUE
LEFT JOIN interaction_channel AS affected_channel_taxonomy
    ON affected_channel_taxonomy.channel_code = affected_channel.channel_code
LEFT JOIN feedback_item_hotspot AS feedback_hotspot
    ON feedback_hotspot.feedback_item_id = item.feedback_item_id
LEFT JOIN hotspot ON hotspot.hotspot_id = feedback_hotspot.hotspot_id
WHERE {{where_clause}}
GROUP BY 1, 2
ORDER BY count DESC, dimension_key
"""

# ``{where_clause}`` and ``{dimension_column}`` are filled only with the
# source-controlled fragments assembled by AnalyticsRepository.
SUMMARY_SQL: Final = f"""
SELECT
    COUNT(DISTINCT item.feedback_item_id) AS total,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'POSITIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN item.feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS csat_score,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'POSITIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN item.feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS positive_rate,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'NEGATIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN item.feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS negative_rate,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'UNKNOWN' THEN item.feedback_item_id END)
        ::double precision / NULLIF(COUNT(DISTINCT item.feedback_item_id), 0),
        0.0
    ) AS sentiment_unknown_rate,
    COUNT(DISTINCT CASE WHEN hotspot.status NOT IN ('RESOLVED', 'DISMISSED') THEN hotspot.hotspot_id END)
        AS active_hotspots
FROM {ANALYTICS_VIEW} AS item
LEFT JOIN feedback_item_hotspot AS feedback_hotspot
    ON feedback_hotspot.feedback_item_id = item.feedback_item_id
LEFT JOIN hotspot ON hotspot.hotspot_id = feedback_hotspot.hotspot_id
WHERE {{where_clause}}
"""

TREND_SQL: Final = f"""
SELECT
    DATE_TRUNC(:grain, item.reported_at) AS time_bucket,
    COUNT(DISTINCT item.feedback_item_id) AS volume,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'NEGATIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(COUNT(DISTINCT CASE WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE') THEN item.feedback_item_id END), 0),
        0.0
    ) AS negative_rate,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'UNKNOWN' THEN item.feedback_item_id END)::double precision
        / NULLIF(COUNT(DISTINCT item.feedback_item_id), 0),
        0.0
    ) AS unknown_rate,
    COUNT(DISTINCT CASE WHEN hotspot.status NOT IN ('RESOLVED', 'DISMISSED') THEN hotspot.hotspot_id END)
        AS active_hotspots
FROM {ANALYTICS_VIEW} AS item
LEFT JOIN feedback_item_hotspot AS feedback_hotspot
    ON feedback_hotspot.feedback_item_id = item.feedback_item_id
LEFT JOIN hotspot ON hotspot.hotspot_id = feedback_hotspot.hotspot_id
WHERE {{where_clause}}
GROUP BY 1
ORDER BY 1
"""

BREAKDOWN_SQL: Final = f"""
SELECT
    COALESCE({{dimension_code_expression}}, 'UNKNOWN') AS dimension_key,
    COALESCE({{dimension_name_expression}}, 'Chưa xác định') AS dimension_name,
    COUNT(DISTINCT item.feedback_item_id) AS count,
    COALESCE(
        COUNT(DISTINCT CASE WHEN item.sentiment = 'NEGATIVE' THEN item.feedback_item_id END)
        ::double precision
        / NULLIF(COUNT(DISTINCT CASE WHEN item.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE') THEN item.feedback_item_id END), 0),
        0.0
    ) AS negative_rate,
    COUNT(DISTINCT CASE WHEN hotspot.status NOT IN ('RESOLVED', 'DISMISSED') THEN hotspot.hotspot_id END)
        AS active_hotspots,
    COALESCE(
        COUNT(DISTINCT item.feedback_item_id)::double precision
        / NULLIF(SUM(COUNT(DISTINCT item.feedback_item_id)) OVER (), 0),
        0.0
    ) AS percentage
FROM {ANALYTICS_VIEW} AS item
LEFT JOIN interaction_channel AS intake_channel
    ON intake_channel.interaction_channel_id = item.intake_channel_id
LEFT JOIN feedback_item_hotspot AS feedback_hotspot
    ON feedback_hotspot.feedback_item_id = item.feedback_item_id
LEFT JOIN hotspot ON hotspot.hotspot_id = feedback_hotspot.hotspot_id
WHERE {{where_clause}}
GROUP BY 1, 2
ORDER BY count DESC, dimension_key
"""

FILTER_OPTIONS_SQL: Final = f"""
SELECT 'source_system' AS option_type, item.source_system AS code,
       item.source_system AS name, NULL::text AS id
FROM {ANALYTICS_VIEW} AS item
WHERE {{where_clause}}
GROUP BY 1, 2, 3, 4
UNION ALL
SELECT 'location' AS option_type, COALESCE(item.location_code, 'UNKNOWN') AS code,
       COALESCE(item.location_name, 'Chưa xác định') AS name,
       item.location_id::text AS id
FROM {ANALYTICS_VIEW} AS item
WHERE {{where_clause}}
GROUP BY 1, 2, 3, 4
ORDER BY option_type, name, code
"""

# Taxonomy-controlled dimensions must not disappear just because the current
# analytics slice has zero matching feedback.  Source systems and locations
# remain data-backed above; they are project-specific rather than canonical
# taxonomy values.
TAXONOMY_FILTER_OPTIONS_SQL: Final = """
WITH published_taxonomy AS (
    SELECT taxonomy_release_id
    FROM taxonomy_release
    WHERE status = 'PUBLISHED'
      AND (effective_from IS NULL OR effective_from <= NOW())
      AND (effective_to IS NULL OR effective_to > NOW())
    ORDER BY effective_from DESC NULLS LAST, published_at DESC NULLS LAST, created_at DESC
    LIMIT 1
)
SELECT 'journey_stage' AS option_type, stage.stage_code AS code,
       stage.name_vi AS name, NULL::text AS id, stage.sort_order AS sort_order
FROM customer_lifecycle_stage AS stage
JOIN published_taxonomy AS taxonomy
  ON taxonomy.taxonomy_release_id = stage.taxonomy_release_id
WHERE stage.active
UNION ALL
SELECT 'journey_step' AS option_type, step.step_code AS code,
       step.name_vi AS name, NULL::text AS id,
       stage.sort_order * 100 + step.sort_order AS sort_order
FROM customer_lifecycle_step AS step
JOIN customer_lifecycle_stage AS stage
  ON stage.customer_lifecycle_stage_id = step.customer_lifecycle_stage_id
JOIN published_taxonomy AS taxonomy
  ON taxonomy.taxonomy_release_id = step.taxonomy_release_id
WHERE step.active AND stage.active
  AND (CAST(:taxonomy_stage_code AS text) IS NULL OR stage.stage_code = CAST(:taxonomy_stage_code AS text))
UNION ALL
SELECT 'service_request_step' AS option_type, step.step_code AS code,
       step.name_vi AS name, NULL::text AS id, step.sort_order AS sort_order
FROM service_request_step AS step
JOIN published_taxonomy AS taxonomy
  ON taxonomy.taxonomy_release_id = step.taxonomy_release_id
WHERE step.active
UNION ALL
SELECT 'service' AS option_type, service.service_code AS code,
       service.name_vi AS name, NULL::text AS id, 0 AS sort_order
FROM service
JOIN published_taxonomy AS taxonomy
  ON taxonomy.taxonomy_release_id = service.taxonomy_release_id
WHERE service.active
UNION ALL
SELECT 'issue' AS option_type, issue.issue_code AS code,
       issue.name_vi AS name, NULL::text AS id, 0 AS sort_order
FROM issue
JOIN service ON service.service_id = issue.service_id
JOIN published_taxonomy AS taxonomy
  ON taxonomy.taxonomy_release_id = issue.taxonomy_release_id
WHERE issue.active AND service.active
  AND (CAST(:taxonomy_service_code AS text) IS NULL OR service.service_code = CAST(:taxonomy_service_code AS text))
UNION ALL
SELECT 'intake_channel' AS option_type, channel.channel_code AS code,
       channel.name_vi AS name, NULL::text AS id, 0 AS sort_order
FROM interaction_channel AS channel
WHERE channel.active
UNION ALL
SELECT 'affected_channel' AS option_type, channel.channel_code AS code,
       channel.name_vi AS name, NULL::text AS id, 0 AS sort_order
FROM interaction_channel AS channel
WHERE channel.active
ORDER BY option_type, sort_order, name, code
"""
