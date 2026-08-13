"""Parameterized PostgreSQL queries over the governed analytics semantic view."""
from __future__ import annotations

from types import MappingProxyType
from typing import Final, Mapping

ANALYTICS_VIEW: Final = "analytics_feedback_item_v1"

# These are SQL identifiers controlled in source, never user-provided values.
BREAKDOWN_DIMENSIONS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "service": "service_code",
        "issue": "issue_code",
        "journey_stage": "customer_lifecycle_stage_code",
        "journey_step": "customer_lifecycle_step_code",
        "service_request_step": "service_request_step_code",
        "location": "location_code",
        "intake_channel": "intake_channel_code",
        "sentiment": "sentiment",
        "severity": "operational_severity",
        # Compatibility with the task wording; API clients should use
        # ``journey_stage``.
        "stage": "customer_lifecycle_stage_code",
    }
)

AFFECTED_CHANNEL_BREAKDOWN_SQL: Final = f"""
SELECT
    COALESCE(affected_channel.channel_code, 'UNKNOWN') AS dimension_key,
    COUNT(DISTINCT item.feedback_item_id) AS count,
    COALESCE(
        COUNT(DISTINCT item.feedback_item_id)::double precision
        / NULLIF(SUM(COUNT(DISTINCT item.feedback_item_id)) OVER (), 0),
        0.0
    ) AS percentage
FROM {ANALYTICS_VIEW} AS item
LEFT JOIN LATERAL UNNEST(item.affected_channel_codes)
    AS affected_channel(channel_code) ON TRUE
WHERE {{where_clause}}
GROUP BY 1
ORDER BY count DESC, dimension_key
"""

# ``{where_clause}`` and ``{dimension_column}`` are filled only with the
# source-controlled fragments assembled by AnalyticsRepository.
SUMMARY_SQL: Final = f"""
SELECT
    COUNT(DISTINCT feedback_item_id) AS total,
    COALESCE(
        COUNT(DISTINCT CASE WHEN sentiment = 'POSITIVE' THEN feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS csat_score,
    COALESCE(
        COUNT(DISTINCT CASE WHEN sentiment = 'POSITIVE' THEN feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS positive_rate,
    COALESCE(
        COUNT(DISTINCT CASE WHEN sentiment = 'NEGATIVE' THEN feedback_item_id END)
        ::double precision
        / NULLIF(
            COUNT(
                DISTINCT CASE
                    WHEN sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
                    THEN feedback_item_id
                END
            ),
            0
        ),
        0.0
    ) AS negative_rate,
    COALESCE(
        COUNT(DISTINCT CASE WHEN sentiment = 'UNKNOWN' THEN feedback_item_id END)
        ::double precision / NULLIF(COUNT(DISTINCT feedback_item_id), 0),
        0.0
    ) AS sentiment_unknown_rate
FROM {ANALYTICS_VIEW}
WHERE {{where_clause}}
"""

TREND_SQL: Final = f"""
SELECT
    DATE_TRUNC(:grain, reported_at) AS time_bucket,
    COUNT(DISTINCT feedback_item_id) AS volume
FROM {ANALYTICS_VIEW}
WHERE {{where_clause}}
GROUP BY 1
ORDER BY 1
"""

BREAKDOWN_SQL: Final = f"""
SELECT
    COALESCE({{dimension_column}}, 'UNKNOWN') AS dimension_key,
    COUNT(DISTINCT feedback_item_id) AS count,
    COALESCE(
        COUNT(DISTINCT feedback_item_id)::double precision
        / NULLIF(SUM(COUNT(DISTINCT feedback_item_id)) OVER (), 0),
        0.0
    ) AS percentage
FROM {ANALYTICS_VIEW}
WHERE {{where_clause}}
GROUP BY 1
ORDER BY count DESC, dimension_key
"""
