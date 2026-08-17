"""Hotspot domain package."""
from packages.domain.hotspot.engine import (
    FeedbackClusterItem,
    HotspotClusterCandidate,
    calculate_action_priority,
    calculate_operational_severity,
    cluster_eligible_items,
    generate_dimension_key,
    parse_severity,
    validate_hotspot_transition,
)
from packages.domain.hotspot.entities import (
    FeedbackItemHotspot,
    Hotspot,
    HotspotRule,
    HotspotTimelineEvent,
)
from packages.domain.hotspot.exceptions import (
    ConcurrencyConflictError,
    HotspotDomainError,
    HotspotNotFoundError,
    InvalidStateTransitionError,
)

__all__ = [
    "Hotspot",
    "FeedbackItemHotspot",
    "HotspotTimelineEvent",
    "HotspotRule",
    "HotspotDomainError",
    "InvalidStateTransitionError",
    "HotspotNotFoundError",
    "ConcurrencyConflictError",
    "FeedbackClusterItem",
    "HotspotClusterCandidate",
    "calculate_action_priority",
    "calculate_operational_severity",
    "cluster_eligible_items",
    "generate_dimension_key",
    "parse_severity",
    "validate_hotspot_transition",
]
