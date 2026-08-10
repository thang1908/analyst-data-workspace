import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from cx_contracts.common.enums import ImportJobState, ImportRowOutcome
from cx_contracts.import_pkg.csv_v1 import EXACT_CSV_V1_HEADERS
from apps.worker.src.modules.imports.retry_policy import apply_job_retry


@pytest.mark.asyncio
async def test_apply_job_retry_validation_phase():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = uuid4()
    mock_job.state = ImportJobState.FAILED
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_result

    updated_job = await apply_job_retry(mock_session, mock_job.id, expected_version=1, phase="VALIDATION")
    assert updated_job.state == ImportJobState.VALIDATING
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_apply_job_retry_execution_phase():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = uuid4()
    mock_job.state = ImportJobState.FAILED
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_result

    updated_job = await apply_job_retry(mock_session, mock_job.id, expected_version=1, phase="EXECUTION")
    assert updated_job.state == ImportJobState.QUEUED
    mock_session.commit.assert_called_once()
