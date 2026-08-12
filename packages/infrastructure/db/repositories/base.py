"""Generic async base repository với các thao tác CRUD dùng chung."""
from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.infrastructure.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic Repository cung cấp các thao tác CRUD bất đồng bộ.

    Cách dùng:
        class FeedbackRepository(BaseRepository[FeedbackItem]):
            def __init__(self, session: AsyncSession):
                super().__init__(FeedbackItem, session)
    """

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, record_id: uuid.UUID) -> ModelT | None:
        """Lấy 1 bản ghi theo Primary Key UUID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalars().first()

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelT]:
        """Lấy danh sách bản ghi có phân trang và lọc cơ bản."""
        stmt = select(self.model)
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, instance: ModelT) -> ModelT:
        """Thêm mới 1 bản ghi vào Database."""
        self.session.add(instance)
        await self.session.flush()  # Ghi vào DB nhưng chưa commit
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT) -> ModelT:
        """Cập nhật bản ghi (instance đã được chỉnh sửa thuộc tính)."""
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete_by_id(self, record_id: uuid.UUID) -> bool:
        """Xóa bản ghi theo ID. Trả về True nếu xóa thành công."""
        instance = await self.get_by_id(record_id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
