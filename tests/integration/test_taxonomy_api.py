"""HTTP contract tests for Taxonomy API endpoints."""
from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from apps.api.deps import get_taxonomy_repository
from apps.api.main import app
from packages.infrastructure.db.repositories.taxonomy import (
    IssueRow,
    ServiceRef,
    ServiceRow,
    StageRow,
    StepRow,
    TouchpointRow,
)


class StubTaxonomyRepository:
    def __init__(self) -> None:
        self.stage_id = uuid4()
        self.step_id = uuid4()
        self.tp_id = uuid4()
        self.svc_id = uuid4()
        self.iss_id = uuid4()

    async def get_published_release_id(self) -> UUID | None:
        return uuid4()

    async def list_stages(self, taxonomy_release_id: UUID | None = None, active: bool = True) -> list[StageRow]:
        return [
            StageRow(
                id=self.stage_id,
                code="RES",
                name_vi="Cư trú",
                name_en="Residence",
                definition="Trải nghiệm trong quá trình sinh sống",
                sort_order=5,
                active=True,
            )
        ]

    async def list_steps(
        self, taxonomy_release_id: UUID | None = None, stage_code: str | None = None, active: bool = True
    ) -> list[StepRow]:
        return [
            StepRow(
                id=self.step_id,
                code="RES-03",
                stage_id=self.stage_id,
                stage_code="RES",
                stage_name_vi="Cư trú",
                name_vi="Ra vào & di chuyển",
                name_en="Access & Mobility",
                definition="Quá trình di chuyển và sử dụng bãi xe",
                sort_order=3,
                active=True,
            )
        ]

    async def list_touchpoints(
        self,
        taxonomy_release_id: UUID | None = None,
        step_code: str | None = None,
        service_code: str | None = None,
        active: bool = True,
    ) -> list[TouchpointRow]:
        return [
            TouchpointRow(
                id=self.tp_id,
                code="TP-RES-03-01",
                name_vi="Quét thẻ & cổng ra vào tòa nhà",
                name_en="Access turnstile & Card scan",
                definition="Quẹt thẻ sảnh, cổng kiểm soát an ninh",
                lifecycle_step_id=self.step_id,
                lifecycle_step_code="RES-03",
                lifecycle_step_name_vi="Ra vào & di chuyển",
                sort_order=1,
                active=True,
                services=[
                    ServiceRef(
                        id=self.svc_id,
                        code="SV-05",
                        name_vi="Ra vào & bãi xe",
                        mapping_type="PRIMARY",
                    )
                ],
            )
        ]

    async def list_services(self, taxonomy_release_id: UUID | None = None, active: bool = True) -> list[ServiceRow]:
        return [
            ServiceRow(
                id=self.svc_id,
                code="SV-05",
                name_vi="Ra vào & bãi xe",
                name_en="Access & Parking",
                default_severity="SEV-3",
                definition="Dịch vụ kiểm soát ra vào và quản lý bãi gửi xe",
                sort_order=5,
                active=True,
            )
        ]

    async def list_issues(
        self,
        taxonomy_release_id: UUID | None = None,
        service_code: str | None = None,
        service_id: UUID | None = None,
        active: bool = True,
    ) -> list[IssueRow]:
        return [
            IssueRow(
                id=self.iss_id,
                code="IS-05-01",
                service_id=self.svc_id,
                service_code="SV-05",
                service_name_vi="Ra vào & bãi xe",
                name_vi="Ra vào hoặc tiếp khách",
                name_en="Access or Visitor",
                safety_critical=False,
                definition="Sự cố quẹt thẻ hoặc đăng ký khách",
                sort_order=1,
                active=True,
            )
        ]


def _client() -> TestClient:
    async def override_repository() -> StubTaxonomyRepository:
        return StubTaxonomyRepository()

    app.dependency_overrides[get_taxonomy_repository] = override_repository
    return TestClient(app)


def test_list_stages_endpoint() -> None:
    client = _client()
    try:
        res = client.get("/api/v1/customer-lifecycle/stages")
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["code"] == "RES"
    assert data[0]["name_vi"] == "Cư trú"


def test_list_steps_endpoint() -> None:
    client = _client()
    try:
        res = client.get("/api/v1/customer-lifecycle/steps?stage_code=RES")
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["code"] == "RES-03"
    assert data[0]["stage"]["code"] == "RES"


def test_list_touchpoints_endpoint() -> None:
    client = _client()
    try:
        res = client.get("/api/v1/customer-lifecycle/touchpoints?step_code=RES-03")
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["code"] == "TP-RES-03-01"
    assert data[0]["lifecycle_step"]["code"] == "RES-03"
    assert len(data[0]["services"]) == 1
    assert data[0]["services"][0]["code"] == "SV-05"


def test_list_services_and_issues_endpoints() -> None:
    client = _client()
    try:
        res_svc = client.get("/api/v1/services")
        res_iss = client.get("/api/v1/issues?service_code=SV-05")
    finally:
        app.dependency_overrides.clear()

    assert res_svc.status_code == 200
    assert res_svc.json()[0]["code"] == "SV-05"

    assert res_iss.status_code == 200
    assert res_iss.json()[0]["code"] == "IS-05-01"
