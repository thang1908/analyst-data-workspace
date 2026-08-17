"""Unit tests for TaxonomyRepository."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from packages.infrastructure.db.repositories.taxonomy import TaxonomyRepository


def _session_returning(rows: list[dict[str, object]]) -> AsyncMock:
    result = MagicMock()
    mappings = result.mappings.return_value
    mappings.all.return_value = rows
    result.scalar_one_or_none.return_value = uuid4()
    session = AsyncMock()
    session.execute = AsyncMock(return_value=result)
    return session


@pytest.mark.asyncio
async def test_list_stages_query() -> None:
    stage_id = uuid4()
    rows = [
        {
            "id": stage_id,
            "code": "RES",
            "name_vi": "Cư trú",
            "name_en": "Residence",
            "definition": "Living experience",
            "sort_order": 5,
            "active": True,
        }
    ]
    session = _session_returning(rows)
    repo = TaxonomyRepository(session)

    stages = await repo.list_stages(taxonomy_release_id=uuid4())
    assert len(stages) == 1
    assert stages[0].code == "RES"
    assert stages[0].name_vi == "Cư trú"


@pytest.mark.asyncio
async def test_list_steps_query() -> None:
    step_id = uuid4()
    stage_id = uuid4()
    rows = [
        {
            "id": step_id,
            "code": "RES-03",
            "stage_id": stage_id,
            "stage_code": "RES",
            "stage_name_vi": "Cư trú",
            "name_vi": "Ra vào & di chuyển",
            "name_en": "Access & Mobility",
            "definition": "Access description",
            "sort_order": 3,
            "active": True,
        }
    ]
    session = _session_returning(rows)
    repo = TaxonomyRepository(session)

    steps = await repo.list_steps(stage_code="RES")
    assert len(steps) == 1
    assert steps[0].code == "RES-03"
    assert steps[0].stage_code == "RES"


@pytest.mark.asyncio
async def test_list_touchpoints_query() -> None:
    tp_id = uuid4()
    step_id = uuid4()
    svc_id = uuid4()

    tp_rows = [
        {
            "id": tp_id,
            "code": "TP-RES-03-01",
            "name_vi": "Quét thẻ & cổng ra vào",
            "name_en": "Card scan",
            "definition": "Def",
            "lifecycle_step_id": step_id,
            "lifecycle_step_code": "RES-03",
            "lifecycle_step_name_vi": "Ra vào",
            "sort_order": 1,
            "active": True,
        }
    ]
    map_rows = [
        {
            "touchpoint_id": tp_id,
            "service_id": svc_id,
            "service_code": "SV-05",
            "name_vi": "Ra vào & bãi xe",
            "mapping_type": "PRIMARY",
        }
    ]

    result1 = MagicMock()
    result1.mappings.return_value.all.return_value = tp_rows

    result2 = MagicMock()
    result2.mappings.return_value.all.return_value = map_rows

    session = AsyncMock()
    session.execute = AsyncMock(side_effect=[MagicMock(scalar_one_or_none=lambda: uuid4()), result1, result2])

    repo = TaxonomyRepository(session)
    tps = await repo.list_touchpoints(step_code="RES-03")
    assert len(tps) == 1
    assert tps[0].code == "TP-RES-03-01"
    assert len(tps[0].services) == 1
    assert tps[0].services[0].code == "SV-05"
