"""SQL repository for taxonomy dimension queries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True, slots=True)
class StageRow:
    id: UUID
    code: str
    name_vi: str
    name_en: str | None
    definition: str | None
    sort_order: int
    active: bool


@dataclass(frozen=True, slots=True)
class StepRow:
    id: UUID
    code: str
    stage_id: UUID
    stage_code: str
    stage_name_vi: str
    name_vi: str
    name_en: str | None
    definition: str | None
    sort_order: int
    active: bool


@dataclass(frozen=True, slots=True)
class ServiceRef:
    id: UUID
    code: str
    name_vi: str
    mapping_type: str


@dataclass(frozen=True, slots=True)
class TouchpointRow:
    id: UUID
    code: str
    name_vi: str
    name_en: str | None
    definition: str | None
    lifecycle_step_id: UUID
    lifecycle_step_code: str
    lifecycle_step_name_vi: str
    sort_order: int
    active: bool
    services: list[ServiceRef]


@dataclass(frozen=True, slots=True)
class ServiceRow:
    id: UUID
    code: str
    name_vi: str
    name_en: str | None
    default_severity: str
    definition: str | None
    sort_order: int
    active: bool


@dataclass(frozen=True, slots=True)
class IssueRow:
    id: UUID
    code: str
    service_id: UUID
    service_code: str
    service_name_vi: str
    name_vi: str
    name_en: str | None
    safety_critical: bool
    definition: str | None
    sort_order: int
    active: bool


class TaxonomyRepository:
    """Read-only access to published and versioned taxonomy entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_published_release_id(self) -> UUID | None:
        result = await self._session.execute(
            text("""
                SELECT taxonomy_release_id
                FROM taxonomy_release
                WHERE status = 'PUBLISHED'
                  AND (effective_from IS NULL OR effective_from <= NOW())
                  AND (effective_to IS NULL OR effective_to > NOW())
                ORDER BY effective_from DESC NULLS LAST, published_at DESC NULLS LAST, created_at DESC
                LIMIT 1
            """)
        )
        row = result.scalar_one_or_none()
        return row

    async def list_stages(
        self, taxonomy_release_id: UUID | None = None, active: bool = True
    ) -> list[StageRow]:
        rel_id = taxonomy_release_id or await self.get_published_release_id()
        if not rel_id:
            return []
        query_str = """
            SELECT customer_lifecycle_stage_id AS id, stage_code AS code,
                   name_vi, name_en, definition, sort_order, active
            FROM customer_lifecycle_stage
            WHERE taxonomy_release_id = :rel_id
        """
        params: dict[str, Any] = {"rel_id": rel_id}
        if active is not None:
            query_str += " AND active = :active"
            params["active"] = active
        query_str += " ORDER BY sort_order, stage_code"

        result = await self._session.execute(text(query_str), params)
        return [
            StageRow(
                id=row["id"],
                code=row["code"],
                name_vi=row["name_vi"],
                name_en=row["name_en"],
                definition=row["definition"],
                sort_order=row["sort_order"],
                active=row["active"],
            )
            for row in result.mappings().all()
        ]

    async def list_steps(
        self,
        taxonomy_release_id: UUID | None = None,
        stage_code: str | None = None,
        active: bool = True,
    ) -> list[StepRow]:
        rel_id = taxonomy_release_id or await self.get_published_release_id()
        if not rel_id:
            return []
        query_str = """
            SELECT step.customer_lifecycle_step_id AS id, step.step_code AS code,
                   step.name_vi, step.name_en, step.definition, step.sort_order, step.active,
                   stage.customer_lifecycle_stage_id AS stage_id, stage.stage_code,
                   stage.name_vi AS stage_name_vi
            FROM customer_lifecycle_step step
            JOIN customer_lifecycle_stage stage
              ON stage.customer_lifecycle_stage_id = step.customer_lifecycle_stage_id
            WHERE step.taxonomy_release_id = :rel_id
        """
        params: dict[str, Any] = {"rel_id": rel_id}
        if stage_code:
            query_str += " AND stage.stage_code = :stage_code"
            params["stage_code"] = stage_code
        if active is not None:
            query_str += " AND step.active = :active"
            params["active"] = active
        query_str += " ORDER BY stage.sort_order, step.sort_order, step.step_code"

        result = await self._session.execute(text(query_str), params)
        return [
            StepRow(
                id=row["id"],
                code=row["code"],
                stage_id=row["stage_id"],
                stage_code=row["stage_code"],
                stage_name_vi=row["stage_name_vi"],
                name_vi=row["name_vi"],
                name_en=row["name_en"],
                definition=row["definition"],
                sort_order=row["sort_order"],
                active=row["active"],
            )
            for row in result.mappings().all()
        ]

    async def list_touchpoints(
        self,
        taxonomy_release_id: UUID | None = None,
        step_code: str | None = None,
        service_code: str | None = None,
        active: bool = True,
    ) -> list[TouchpointRow]:
        rel_id = taxonomy_release_id or await self.get_published_release_id()
        if not rel_id:
            return []
        query_str = """
            SELECT tp.touchpoint_id AS id, tp.touchpoint_code AS code,
                   tp.name_vi, tp.name_en, tp.definition, tp.sort_order, tp.active,
                   step.customer_lifecycle_step_id AS lifecycle_step_id,
                   step.step_code AS lifecycle_step_code,
                   step.name_vi AS lifecycle_step_name_vi
            FROM touchpoint tp
            JOIN customer_lifecycle_step step
              ON step.customer_lifecycle_step_id = tp.customer_lifecycle_step_id
            WHERE tp.taxonomy_release_id = :rel_id
        """
        params: dict[str, Any] = {"rel_id": rel_id}
        if step_code:
            query_str += " AND step.step_code = :step_code"
            params["step_code"] = step_code
        if active is not None:
            query_str += " AND tp.active = :active"
            params["active"] = active
        if service_code:
            query_str += """ AND EXISTS (
                SELECT 1 FROM touchpoint_service_map tsm
                JOIN service svc ON svc.service_id = tsm.service_id
                WHERE tsm.touchpoint_id = tp.touchpoint_id
                  AND svc.service_code = :service_code
                  AND tsm.active = true
            )"""
            params["service_code"] = service_code
        query_str += " ORDER BY step.sort_order, tp.sort_order, tp.touchpoint_code"

        result = await self._session.execute(text(query_str), params)
        tp_rows = result.mappings().all()
        if not tp_rows:
            return []

        # Load service mappings
        map_result = await self._session.execute(
            text("""
                SELECT tsm.touchpoint_id, svc.service_id, svc.service_code, svc.name_vi, tsm.mapping_type
                FROM touchpoint_service_map tsm
                JOIN service svc ON svc.service_id = tsm.service_id
                WHERE tsm.taxonomy_release_id = :rel_id
                  AND tsm.active = true
                ORDER BY tsm.mapping_type DESC, svc.sort_order
            """),
            {"rel_id": rel_id},
        )
        svc_by_tp: dict[UUID, list[ServiceRef]] = {}
        for map_row in map_result.mappings().all():
            svc_by_tp.setdefault(map_row["touchpoint_id"], []).append(
                ServiceRef(
                    id=map_row["service_id"],
                    code=map_row["service_code"],
                    name_vi=map_row["name_vi"],
                    mapping_type=map_row["mapping_type"],
                )
            )

        return [
            TouchpointRow(
                id=row["id"],
                code=row["code"],
                name_vi=row["name_vi"],
                name_en=row["name_en"],
                definition=row["definition"],
                lifecycle_step_id=row["lifecycle_step_id"],
                lifecycle_step_code=row["lifecycle_step_code"],
                lifecycle_step_name_vi=row["lifecycle_step_name_vi"],
                sort_order=row["sort_order"],
                active=row["active"],
                services=svc_by_tp.get(row["id"], []),
            )
            for row in tp_rows
        ]

    async def list_services(
        self, taxonomy_release_id: UUID | None = None, active: bool = True
    ) -> list[ServiceRow]:
        rel_id = taxonomy_release_id or await self.get_published_release_id()
        if not rel_id:
            return []
        query_str = """
            SELECT service_id AS id, service_code AS code, name_vi, name_en,
                   default_severity, definition, sort_order, active
            FROM service
            WHERE taxonomy_release_id = :rel_id
        """
        params: dict[str, Any] = {"rel_id": rel_id}
        if active is not None:
            query_str += " AND active = :active"
            params["active"] = active
        query_str += " ORDER BY sort_order, service_code"

        result = await self._session.execute(text(query_str), params)
        return [
            ServiceRow(
                id=row["id"],
                code=row["code"],
                name_vi=row["name_vi"],
                name_en=row["name_en"],
                default_severity=row["default_severity"],
                definition=row["definition"],
                sort_order=row["sort_order"],
                active=row["active"],
            )
            for row in result.mappings().all()
        ]

    async def list_issues(
        self,
        taxonomy_release_id: UUID | None = None,
        service_code: str | None = None,
        service_id: UUID | None = None,
        active: bool = True,
    ) -> list[IssueRow]:
        rel_id = taxonomy_release_id or await self.get_published_release_id()
        if not rel_id:
            return []
        query_str = """
            SELECT issue.issue_id AS id, issue.issue_code AS code,
                   issue.name_vi, issue.name_en, issue.safety_critical,
                   issue.definition, issue.sort_order, issue.active,
                   service.service_id, service.service_code, service.name_vi AS service_name_vi
            FROM issue
            JOIN service ON service.service_id = issue.service_id
            WHERE issue.taxonomy_release_id = :rel_id
        """
        params: dict[str, Any] = {"rel_id": rel_id}
        if service_code:
            query_str += " AND service.service_code = :service_code"
            params["service_code"] = service_code
        if service_id:
            query_str += " AND service.service_id = :service_id"
            params["service_id"] = service_id
        if active is not None:
            query_str += " AND issue.active = :active"
            params["active"] = active
        query_str += " ORDER BY service.sort_order, issue.sort_order, issue.issue_code"

        result = await self._session.execute(text(query_str), params)
        return [
            IssueRow(
                id=row["id"],
                code=row["code"],
                service_id=row["service_id"],
                service_code=row["service_code"],
                service_name_vi=row["service_name_vi"],
                name_vi=row["name_vi"],
                name_en=row["name_en"],
                safety_critical=row["safety_critical"],
                definition=row["definition"],
                sort_order=row["sort_order"],
                active=row["active"],
            )
            for row in result.mappings().all()
        ]

