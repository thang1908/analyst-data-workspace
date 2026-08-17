"""Unit tests for Touchpoint and Step-Touchpoint-Service mapping domain entities."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from packages.domain.shared.enums import MappingType
from packages.domain.taxonomy.entities import (
    CustomerLifecycleStage,
    CustomerLifecycleStep,
    Issue,
    Service,
    Touchpoint,
    TouchpointServiceMap,
)


def test_touchpoint_entity_creation() -> None:
    rel_id = uuid4()
    step_id = uuid4()
    tp_id = uuid4()
    now = datetime.now(timezone.utc)

    tp = Touchpoint(
        touchpoint_id=tp_id,
        taxonomy_release_id=rel_id,
        customer_lifecycle_step_id=step_id,
        touchpoint_code="TP-RES-02-01",
        name_vi="Gửi yêu cầu trên app",
        name_en="Resident app ticket",
        definition="Gửi phản ánh hoặc nhận thông báo qua ứng dụng cư dân",
        sort_order=1,
        active=True,
        active_from=now,
        active_to=None,
    )

    assert tp.touchpoint_id == tp_id
    assert tp.touchpoint_code == "TP-RES-02-01"
    assert tp.customer_lifecycle_step_id == step_id
    assert tp.active is True
    assert tp.active_from == now
    assert tp.active_to is None


def test_touchpoint_service_map_entity() -> None:
    rel_id = uuid4()
    tp_id = uuid4()
    svc_id = uuid4()
    map_id = uuid4()

    tsm_primary = TouchpointServiceMap(
        touchpoint_service_map_id=map_id,
        taxonomy_release_id=rel_id,
        touchpoint_id=tp_id,
        service_id=svc_id,
        mapping_type=MappingType.PRIMARY,
        active=True,
    )

    assert tsm_primary.mapping_type == MappingType.PRIMARY
    assert tsm_primary.active is True

    tsm_secondary = TouchpointServiceMap(
        touchpoint_service_map_id=uuid4(),
        taxonomy_release_id=rel_id,
        touchpoint_id=tp_id,
        service_id=uuid4(),
        mapping_type=MappingType.SECONDARY,
        active=True,
    )

    assert tsm_secondary.mapping_type == MappingType.SECONDARY
