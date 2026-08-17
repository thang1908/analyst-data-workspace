"""Taxonomy read endpoints exposing stages, steps, touchpoints, services, and issues."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from apps.api.deps import get_taxonomy_repository
from apps.api.schemas.taxonomy import (
    IssueResponseItem,
    ReferenceItem,
    ServiceResponseItem,
    StageResponseItem,
    StepResponseItem,
    TouchpointResponseItem,
    TouchpointServiceItem,
)
from packages.infrastructure.db.repositories.taxonomy import (
    IssueRow,
    ServiceRow,
    StageRow,
    StepRow,
    TaxonomyRepository,
    TouchpointRow,
)

router = APIRouter(prefix="/api/v1", tags=["Taxonomy"])
TaxonomyRepositoryDep = Annotated[TaxonomyRepository, Depends(get_taxonomy_repository)]


@router.get(
    "/customer-lifecycle/stages",
    response_model=list[StageResponseItem],
    operation_id="listCustomerLifecycleStages",
)
async def list_stages(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    active: bool = True,
) -> list[StageResponseItem]:
    rows = await repository.list_stages(taxonomy_release_id=taxonomy_release_id, active=active)
    return [
        StageResponseItem(
            id=r.id,
            code=r.code,
            name_vi=r.name_vi,
            name_en=r.name_en,
            definition=r.definition,
            sort_order=r.sort_order,
        )
        for r in rows
    ]


@router.get(
    "/customer-lifecycle/steps",
    response_model=list[StepResponseItem],
    operation_id="listCustomerLifecycleSteps",
)
async def list_steps(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    stage_code: str | None = None,
    active: bool = True,
) -> list[StepResponseItem]:
    rows = await repository.list_steps(
        taxonomy_release_id=taxonomy_release_id, stage_code=stage_code, active=active
    )
    return [
        StepResponseItem(
            id=r.id,
            code=r.code,
            stage=ReferenceItem(id=r.stage_id, code=r.stage_code, name_vi=r.stage_name_vi),
            name_vi=r.name_vi,
            name_en=r.name_en,
            definition=r.definition,
            sort_order=r.sort_order,
        )
        for r in rows
    ]


@router.get(
    "/customer-lifecycle/touchpoints",
    response_model=list[TouchpointResponseItem],
    operation_id="listCustomerLifecycleTouchpoints",
)
async def list_touchpoints(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    step_code: str | None = None,
    service_code: str | None = None,
    active: bool = True,
) -> list[TouchpointResponseItem]:
    rows = await repository.list_touchpoints(
        taxonomy_release_id=taxonomy_release_id,
        step_code=step_code,
        service_code=service_code,
        active=active,
    )
    return [
        TouchpointResponseItem(
            id=r.id,
            code=r.code,
            name_vi=r.name_vi,
            name_en=r.name_en,
            definition=r.definition,
            lifecycle_step=ReferenceItem(
                id=r.lifecycle_step_id,
                code=r.lifecycle_step_code,
                name_vi=r.lifecycle_step_name_vi,
            ),
            services=[
                TouchpointServiceItem(
                    id=s.id,
                    code=s.code,
                    name_vi=s.name_vi,
                    mapping_type=s.mapping_type,
                )
                for s in r.services
            ],
            sort_order=r.sort_order,
            active=r.active,
        )
        for r in rows
    ]


@router.get(
    "/touchpoints",
    response_model=list[TouchpointResponseItem],
    operation_id="listTouchpointsAlias",
    include_in_schema=False,
)
async def list_touchpoints_alias(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    step_code: str | None = None,
    service_code: str | None = None,
    active: bool = True,
) -> list[TouchpointResponseItem]:
    return await list_touchpoints(
        repository=repository,
        taxonomy_release_id=taxonomy_release_id,
        step_code=step_code,
        service_code=service_code,
        active=active,
    )


@router.get(
    "/services",
    response_model=list[ServiceResponseItem],
    operation_id="listServices",
)
async def list_services(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    active: bool = True,
) -> list[ServiceResponseItem]:
    rows = await repository.list_services(taxonomy_release_id=taxonomy_release_id, active=active)
    return [
        ServiceResponseItem(
            id=r.id,
            code=r.code,
            name_vi=r.name_vi,
            name_en=r.name_en,
            default_severity=r.default_severity,
            definition=r.definition,
            sort_order=r.sort_order,
        )
        for r in rows
    ]


@router.get(
    "/services/{service_id}/issues",
    response_model=list[IssueResponseItem],
    operation_id="listServiceIssues",
)
async def list_service_issues(
    service_id: UUID,
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    active: bool = True,
) -> list[IssueResponseItem]:
    rows = await repository.list_issues(
        taxonomy_release_id=taxonomy_release_id, service_id=service_id, active=active
    )
    return [
        IssueResponseItem(
            id=r.id,
            code=r.code,
            service=ReferenceItem(id=r.service_id, code=r.service_code, name_vi=r.service_name_vi),
            name_vi=r.name_vi,
            name_en=r.name_en,
            safety_critical=r.safety_critical,
            definition=r.definition,
            sort_order=r.sort_order,
        )
        for r in rows
    ]


@router.get(
    "/issues",
    response_model=list[IssueResponseItem],
    operation_id="listIssues",
)
async def list_issues(
    repository: TaxonomyRepositoryDep,
    taxonomy_release_id: UUID | None = None,
    service_code: str | None = None,
    active: bool = True,
) -> list[IssueResponseItem]:
    rows = await repository.list_issues(
        taxonomy_release_id=taxonomy_release_id, service_code=service_code, active=active
    )
    return [
        IssueResponseItem(
            id=r.id,
            code=r.code,
            service=ReferenceItem(id=r.service_id, code=r.service_code, name_vi=r.service_name_vi),
            name_vi=r.name_vi,
            name_en=r.name_en,
            safety_critical=r.safety_critical,
            definition=r.definition,
            sort_order=r.sort_order,
        )
        for r in rows
    ]
