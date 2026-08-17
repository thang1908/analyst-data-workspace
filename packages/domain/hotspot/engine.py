"""Deterministic Hotspot clustering engine and state transition rules."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Sequence
from uuid import UUID

from packages.domain.hotspot.exceptions import InvalidStateTransitionError
from packages.domain.shared.enums import ActionPriority, HotspotStatus, OperationalSeverity

_SEVERITY_ORDER = {
    OperationalSeverity.SEV_1: 4,
    OperationalSeverity.SEV_2: 3,
    OperationalSeverity.SEV_3: 2,
    OperationalSeverity.SEV_4: 1,
}

_SEVERITY_STR_MAP = {
    "SEV-1": OperationalSeverity.SEV_1,
    "SEV-2": OperationalSeverity.SEV_2,
    "SEV-3": OperationalSeverity.SEV_3,
    "SEV-4": OperationalSeverity.SEV_4,
}


def parse_severity(val: str | OperationalSeverity | None) -> OperationalSeverity:
    if isinstance(val, OperationalSeverity):
        return val
    if isinstance(val, str) and val in _SEVERITY_STR_MAP:
        return _SEVERITY_STR_MAP[val]
    return OperationalSeverity.SEV_4


def calculate_operational_severity(severities: Iterable[str | OperationalSeverity]) -> OperationalSeverity:
    """Take the maximum severity observed in a cluster."""
    parsed = [parse_severity(s) for s in severities]
    if not parsed:
        return OperationalSeverity.SEV_4
    return max(parsed, key=lambda s: _SEVERITY_ORDER.get(s, 0))


def calculate_action_priority(
    severities: Sequence[str | OperationalSeverity],
    *,
    count: int = 1,
    is_safety_critical: bool = False,
    safety_playbook_approved: bool = False,
) -> ActionPriority:
    """Categorize action priority according to doc 08 rules.

    IMMEDIATE: Safety/life-safety SEV-1 hard trigger with approved safety playbook.
    URGENT: SEV-2 or unapproved safety SEV-1 or high velocity (count >= 10).
    PLANNED: Repeated SEV-3 / SEV-4 without safety signal.
    MONITOR: Low volume or non-critical signals.
    """
    max_sev = calculate_operational_severity(severities) if severities else OperationalSeverity.SEV_4

    if max_sev == OperationalSeverity.SEV_1 and is_safety_critical:
        if safety_playbook_approved:
            return ActionPriority.IMMEDIATE
        return ActionPriority.URGENT

    if max_sev == OperationalSeverity.SEV_1 or max_sev == OperationalSeverity.SEV_2 or count >= 10:
        return ActionPriority.URGENT

    if max_sev in (OperationalSeverity.SEV_3, OperationalSeverity.SEV_4) and count >= 2:
        return ActionPriority.PLANNED

    return ActionPriority.MONITOR


def generate_dimension_key(
    service_id_or_code: UUID | str,
    issue_id_or_code: UUID | str,
    location_id_or_code: UUID | str | None,
    rule_version: str,
) -> str:
    """Deterministic composite key for idempotency."""
    loc = str(location_id_or_code) if location_id_or_code else "GLOBAL"
    return f"{service_id_or_code}:{issue_id_or_code}:{loc}:{rule_version}"


# Valid state transitions
_ALLOWED_TRANSITIONS: dict[HotspotStatus, set[HotspotStatus]] = {
    HotspotStatus.CANDIDATE: {
        HotspotStatus.CANDIDATE,
        HotspotStatus.ACKNOWLEDGED,
        HotspotStatus.INVESTIGATING,
        HotspotStatus.DISMISSED,
    },
    HotspotStatus.ACKNOWLEDGED: {
        HotspotStatus.ACKNOWLEDGED,
        HotspotStatus.INVESTIGATING,
        HotspotStatus.RESOLVED,
        HotspotStatus.DISMISSED,
    },
    HotspotStatus.INVESTIGATING: {
        HotspotStatus.INVESTIGATING,
        HotspotStatus.RESOLVED,
        HotspotStatus.DISMISSED,
    },
    HotspotStatus.RESOLVED: {
        HotspotStatus.RESOLVED,
        HotspotStatus.REOPENED,
        HotspotStatus.INVESTIGATING,
    },
    HotspotStatus.DISMISSED: {
        HotspotStatus.DISMISSED,
        HotspotStatus.REOPENED,
        HotspotStatus.INVESTIGATING,
    },
    HotspotStatus.REOPENED: {
        HotspotStatus.REOPENED,
        HotspotStatus.INVESTIGATING,
        HotspotStatus.RESOLVED,
        HotspotStatus.DISMISSED,
    },
}


def validate_hotspot_transition(
    from_status: HotspotStatus | str,
    to_status: HotspotStatus | str,
    *,
    reason: str | None = None,
    resolution_summary: str | None = None,
) -> None:
    """Validate lifecycle state transition and required justification."""
    src = HotspotStatus(from_status) if isinstance(from_status, str) else from_status
    dst = HotspotStatus(to_status) if isinstance(to_status, str) else to_status

    allowed = _ALLOWED_TRANSITIONS.get(src, set())
    if dst not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition Hotspot from {src.value} to {dst.value}. "
            f"Allowed transitions: {', '.join(s.value for s in allowed if s != src)}"
        )

    if dst == HotspotStatus.DISMISSED and (not reason or not reason.strip()):
        raise InvalidStateTransitionError("A reason is required to dismiss a hotspot.")

    if dst == HotspotStatus.RESOLVED and not (
        (resolution_summary and resolution_summary.strip()) or (reason and reason.strip())
    ):
        raise InvalidStateTransitionError("A resolution summary or reason is required to resolve a hotspot.")

    if dst == HotspotStatus.REOPENED and (not reason or not reason.strip()):
        raise InvalidStateTransitionError("A reason is required to reopen a hotspot.")


@dataclass(frozen=True, slots=True)
class FeedbackClusterItem:
    feedback_item_id: UUID
    reported_at: datetime
    operational_severity: OperationalSeverity | str
    service_id: UUID
    issue_id: UUID
    location_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class HotspotClusterCandidate:
    dimension_key: str
    service_id: UUID
    issue_id: UUID
    location_id: UUID | None
    window_start: datetime
    window_end: datetime
    items: tuple[FeedbackClusterItem, ...]
    operational_severity: OperationalSeverity
    action_priority: ActionPriority
    first_seen_at: datetime
    last_seen_at: datetime

    @property
    def evidence_count(self) -> int:
        return len(self.items)


def cluster_eligible_items(
    items: Iterable[FeedbackClusterItem],
    *,
    window_start: datetime,
    window_end: datetime,
    threshold_count: int = 3,
    rule_version: str = "1.0.0",
    safety_critical_issue_ids: set[UUID] | None = None,
    safety_playbook_approved: bool = False,
) -> list[HotspotClusterCandidate]:
    """Group feedback items deterministically into hotspot candidates meeting threshold."""
    groups: dict[tuple[UUID, UUID, UUID | None], list[FeedbackClusterItem]] = {}
    for item in items:
        key = (item.service_id, item.issue_id, item.location_id)
        groups.setdefault(key, []).append(item)

    safety_set = safety_critical_issue_ids or set()
    clusters: list[HotspotClusterCandidate] = []

    for (service_id, issue_id, location_id), group_items in groups.items():
        if len(group_items) < threshold_count:
            continue

        severities = [it.operational_severity for it in group_items]
        max_sev = calculate_operational_severity(severities)
        is_safety = issue_id in safety_set
        action_prio = calculate_action_priority(
            severities,
            count=len(group_items),
            is_safety_critical=is_safety,
            safety_playbook_approved=safety_playbook_approved,
        )

        dim_key = generate_dimension_key(service_id, issue_id, location_id, rule_version)
        reported_times = [it.reported_at for it in group_items]
        first_seen = min(reported_times)
        last_seen = max(reported_times)

        clusters.append(
            HotspotClusterCandidate(
                dimension_key=dim_key,
                service_id=service_id,
                issue_id=issue_id,
                location_id=location_id,
                window_start=window_start,
                window_end=window_end,
                items=tuple(group_items),
                operational_severity=max_sev,
                action_priority=action_prio,
                first_seen_at=first_seen,
                last_seen_at=last_seen,
            )
        )

    # Deterministic sort by evidence_count DESC, last_seen_at DESC, dimension_key
    clusters.sort(key=lambda c: (-c.evidence_count, c.dimension_key))
    return clusters
