"""Async database session factory and dependency provider."""
from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Lấy chuỗi kết nối Async từ biến môi trường
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "postgresql+psycopg://cx_user:cx_password@localhost:5432/cx_intelligence",
)

# Khởi tạo Async Engine kết nối PostgreSQL
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi dùng
)

# Khởi tạo Async Session Maker dùng chung toàn hệ thống
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency cung cấp Async DB Session cho từng request.

    Cách dùng trong FastAPI Router:
        async def my_route(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
