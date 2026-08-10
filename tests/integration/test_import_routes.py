from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from apps.api.src.app import app

client = TestClient(app)


def test_health_endpoints():
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "UP"

    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "READY"


def test_create_import_job_missing_idempotency_key():
    res = client.post("/api/v1/import-jobs")
    assert res.status_code == 422  # Missing required headers/form data


def test_get_nonexistent_import_job():
    fake_id = str(uuid4())
    res = client.get(f"/api/v1/import-jobs/{fake_id}")
    assert res.status_code == 404
