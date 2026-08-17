"""Unit tests for deterministic Hotspot clustering engine and lifecycle state machine."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from packages.domain.hotspot.engine import (
    FeedbackClusterItem,
    calculate_action_priority,
    calculate_operational_severity,
    cluster_eligible_items,
    generate_dimension_key,
    parse_severity,
    validate_hotspot_transition,
)
from packages.domain.hotspot.exceptions import InvalidStateTransitionError
from packages.domain.shared.enums import ActionPriority, HotspotStatus, OperationalSeverity


def test_severity_calculation_takes_maximum_severity() -> None:
    assert calculate_operational_severity(["SEV-4", "SEV-3", "SEV-4"]) == OperationalSeverity.SEV_3
    assert calculate_operational_severity(["SEV-4", "SEV-1", "SEV-2"]) == OperationalSeverity.SEV_1
    assert calculate_operational_severity(["SEV-4", "SEV-4"]) == OperationalSeverity.SEV_4
    assert calculate_operational_severity([]) == OperationalSeverity.SEV_4


def test_action_priority_categorization() -> None:
    # SEV-1 safety critical with approved safety playbook -> IMMEDIATE
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_1],
            count=3,
            is_safety_critical=True,
            safety_playbook_approved=True,
        )
        == ActionPriority.IMMEDIATE
    )

    # SEV-1 safety critical WITHOUT approved playbook -> URGENT (per P0 spec)
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_1],
            count=3,
            is_safety_critical=True,
            safety_playbook_approved=False,
        )
        == ActionPriority.URGENT
    )

    # SEV-2 -> URGENT
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_2, OperationalSeverity.SEV_3],
            count=3,
        )
        == ActionPriority.URGENT
    )

    # High volume (count >= 10) even with SEV-3 -> URGENT
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_3] * 10,
            count=10,
        )
        == ActionPriority.URGENT
    )

    # Repeated SEV-3/SEV-4 (count >= 2) without safety -> PLANNED
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_3, OperationalSeverity.SEV_4],
            count=2,
        )
        == ActionPriority.PLANNED
    )

    # Single item or low count -> MONITOR
    assert (
        calculate_action_priority(
            [OperationalSeverity.SEV_4],
            count=1,
        )
        == ActionPriority.MONITOR
    )


def test_dimension_key_generation_is_deterministic() -> None:
    svc_id = uuid4()
    iss_id = uuid4()
    loc_id = uuid4()

    key1 = generate_dimension_key(svc_id, iss_id, loc_id, "1.0.0")
    key2 = generate_dimension_key(svc_id, iss_id, loc_id, "1.0.0")
    assert key1 == key2
    assert f"{svc_id}:{iss_id}:{loc_id}:1.0.0" == key1

    key_global = generate_dimension_key(svc_id, iss_id, None, "1.0.0")
    assert f"{svc_id}:{iss_id}:GLOBAL:1.0.0" == key_global


def test_clustering_filters_below_threshold() -> None:
    svc_id = uuid4()
    iss_id = uuid4()
    loc_id = uuid4()
    now = datetime.now(timezone.utc)

    items = [
        FeedbackClusterItem(
            feedback_item_id=uuid4(),
            reported_at=now,
            operational_severity=OperationalSeverity.SEV_2,
            service_id=svc_id,
            issue_id=iss_id,
            location_id=loc_id,
        ),
        FeedbackClusterItem(
            feedback_item_id=uuid4(),
            reported_at=now,
            operational_severity=OperationalSeverity.SEV_3,
            service_id=svc_id,
            issue_id=iss_id,
            location_id=loc_id,
        ),
    ]

    # Threshold 3 -> not enough items
    clusters = cluster_eligible_items(
        items,
        window_start=now,
        window_end=now,
        threshold_count=3,
    )
    assert len(clusters) == 0

    # Threshold 2 -> matches cluster
    clusters = cluster_eligible_items(
        items,
        window_start=now,
        window_end=now,
        threshold_count=2,
    )
    assert len(clusters) == 1
    c = clusters[0]
    assert c.evidence_count == 2
    assert c.operational_severity == OperationalSeverity.SEV_2
    assert c.action_priority == ActionPriority.URGENT
    assert c.service_id == svc_id
    assert c.issue_id == iss_id
    assert c.location_id == loc_id


def test_lifecycle_state_machine_transitions() -> None:
    # Valid transitions
    validate_hotspot_transition(HotspotStatus.CANDIDATE, HotspotStatus.ACKNOWLEDGED)
    validate_hotspot_transition(HotspotStatus.CANDIDATE, HotspotStatus.INVESTIGATING)
    validate_hotspot_transition(HotspotStatus.CANDIDATE, HotspotStatus.DISMISSED, reason="False positive signal")

    validate_hotspot_transition(HotspotStatus.ACKNOWLEDGED, HotspotStatus.INVESTIGATING)
    validate_hotspot_transition(HotspotStatus.ACKNOWLEDGED, HotspotStatus.RESOLVED, resolution_summary="Fixed issue")
    validate_hotspot_transition(HotspotStatus.ACKNOWLEDGED, HotspotStatus.DISMISSED, reason="Not actionable")

    validate_hotspot_transition(HotspotStatus.INVESTIGATING, HotspotStatus.RESOLVED, resolution_summary="Fixed issue")
    validate_hotspot_transition(HotspotStatus.INVESTIGATING, HotspotStatus.DISMISSED, reason="Not an issue")

    validate_hotspot_transition(HotspotStatus.RESOLVED, HotspotStatus.REOPENED, reason="Issue recurred")
    validate_hotspot_transition(HotspotStatus.DISMISSED, HotspotStatus.REOPENED, reason="New evidence")
    validate_hotspot_transition(HotspotStatus.REOPENED, HotspotStatus.INVESTIGATING)


def test_lifecycle_state_machine_invalid_transitions() -> None:
    # CANDIDATE cannot jump directly to RESOLVED without acknowledgement / triage
    with pytest.raises(InvalidStateTransitionError):
        validate_hotspot_transition(HotspotStatus.CANDIDATE, HotspotStatus.RESOLVED)

    # DISMISSED requires a reason
    with pytest.raises(InvalidStateTransitionError):
        validate_hotspot_transition(HotspotStatus.ACKNOWLEDGED, HotspotStatus.DISMISSED, reason="")

    # RESOLVED requires resolution_summary
    with pytest.raises(InvalidStateTransitionError):
        validate_hotspot_transition(HotspotStatus.INVESTIGATING, HotspotStatus.RESOLVED, resolution_summary="")

    # REOPENED requires a reason
    with pytest.raises(InvalidStateTransitionError):
        validate_hotspot_transition(HotspotStatus.RESOLVED, HotspotStatus.REOPENED, reason="")
