"""Unit tests cho Infrastructure Layer — Task #6."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from packages.infrastructure.storage.s3 import S3StorageAdapter


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def generate_presigned_url(self, action: str, **kwargs: object) -> str:
        self.calls.append((action, kwargs))
        return f"https://storage.test/{kwargs['Params']['Key']}?action={action}"

    def delete_object(self, **kwargs: object) -> None:
        self.calls.append(("delete_object", kwargs))


# ─────────────────────────────────────────────────────────────
# Test: S3StorageAdapter
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_s3_generate_presigned_url_contains_object_name() -> None:
    """URL được tạo phải chứa tên file và action đúng."""
    adapter = S3StorageAdapter(client=FakeS3Client())
    url = await adapter.generate_presigned_url("imports/test_file.csv", "get_object")
    assert "imports/test_file.csv" in url
    assert "get_object" in url


@pytest.mark.asyncio
async def test_s3_generate_presigned_url_for_upload() -> None:
    """URL upload (put_object) phải khác URL download (get_object)."""
    adapter = S3StorageAdapter(client=FakeS3Client())
    download_url = await adapter.generate_presigned_url("test.csv", "get_object")
    upload_url = await adapter.generate_presigned_url("test.csv", "put_object")
    assert "get_object" in download_url
    assert "put_object" in upload_url


@pytest.mark.asyncio
async def test_s3_delete_object_returns_true() -> None:
    """Hàm delete_object trả về True khi không có lỗi."""
    adapter = S3StorageAdapter(client=FakeS3Client())
    result = await adapter.delete_object("imports/old_file.csv")
    assert result is True


# ─────────────────────────────────────────────────────────────
# Test: BaseRepository
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_base_repository_get_by_id_returns_none_when_not_found() -> None:
    """get_by_id trả về None khi không tìm thấy bản ghi."""
    from packages.infrastructure.db.repositories.base import BaseRepository

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Patch sqlalchemy select để tránh lỗi coercion khi dùng MagicMock
    with patch("packages.infrastructure.db.repositories.base.select") as mock_select:
        mock_select.return_value.where.return_value = MagicMock()

        from packages.infrastructure.db.base import Base
        from sqlalchemy.orm import mapped_column, Mapped
        import uuid

        # Dùng MagicMock đơn giản chỉ để tạo Repository
        mock_model = MagicMock()

        repo = BaseRepository(mock_model, mock_session)
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None
