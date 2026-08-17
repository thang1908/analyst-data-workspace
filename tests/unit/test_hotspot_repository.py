"""Unit tests for HotspotRepository queries, mutations, and concurrency."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from packages.domain.hotspot.exceptions import ConcurrencyConflictError, HotspotNotFoundError
from packages.infrastructure.db.repositories.hotspot import HotspotListFilters, HotspotRepository


@pytest.mark.asyncio
async def test_list_hotspots_returns_sorted_items() -> None:
    now = datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)
    h_id = uuid4()
    p_id = uuid4()
    s_id = uuid4()
    i_id = uuid4()

    row = {
        "hotspot_id": h_id,
        "project_id": p_id,
        "dimension_key": "SV-05:IS-05-01:GLOBAL:1.0.0",
        "service_id": s_id,
        "service_code": "SV-05",
        "service_name_vi": "Ra vào & bãi xe",
        "issue_id": i_id,
        "issue_code": "IS-05-01",
        "issue_name_vi": "Ra vào hoặc tiếp khách",
        "location_id": None,
        "location_code": None,
        "location_name": None,
        "status": "CANDIDATE",
        "action_priority": "URGENT",
        "operational_severity": "SEV-2",
        "evidence_count": 5,
        "assigned_user_id": None,
        "assigned_team_key": None,
        "first_seen_at": now,
        "last_seen_at": now,
        "resolved_at": None,
        "resolution_summary": None,
        "window_start": now,
        "window_end": now,
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }

    count_res = MagicMock()
    count_res.scalar_one.return_value = 1

    data_res = MagicMock()
    data_res.mappings.return_value.all.return_value = [row]

    session = AsyncMock()
    session.execute = AsyncMock(side_effect=[count_res, data_res])

    repo = HotspotRepository(session)
    items, total = await repo.list_hotspots(HotspotListFilters(project_id=p_id))

    assert total == 1
    assert len(items) == 1
    assert items[0].hotspot_id == h_id
    assert items[0].action_priority == "URGENT"
    assert items[0].service_code == "SV-05"


@pytest.mark.asyncio
async def test_mutate_hotspot_status_checks_optimistic_concurrency() -> None:
    h_id = uuid4()

    # Current version is 2, expected version is 1 -> Conflict
    curr_res = MagicMock()
    curr_res.mappings.return_value.one_or_none.return_value = {"status": "CANDIDATE", "version": 2}

    session = AsyncMock()
    session.execute = AsyncMock(return_value=curr_res)

    repo = HotspotRepository(session)
    with pytest.raises(ConcurrencyConflictError):
        await repo.mutate_hotspot_status(
            h_id,
            action="ACKNOWLEDGE",
            to_status="ACKNOWLEDGED",
            actor_user_id=uuid4(),
            expected_version=1,
        )


@pytest.mark.asyncio
async def test_mutate_hotspot_not_found() -> None:
    h_id = uuid4()

    curr_res = MagicMock()
    curr_res.mappings.return_value.one_or_none.return_value = None

    session = AsyncMock()
    session.execute = AsyncMock(return_value=curr_res)

    repo = HotspotRepository(session)
    with pytest.raises(HotspotNotFoundError):
        await repo.mutate_hotspot_status(
            h_id,
            action="ACKNOWLEDGE",
            to_status="ACKNOWLEDGED",
            actor_user_id=uuid4(),
        )
