"""Object Storage adapter (S3-compatible) với interface chuẩn."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod


class StoragePort(ABC):
    """Interface chuẩn cho Object Storage — các adapter khác cần implement."""

    @abstractmethod
    async def generate_presigned_url(
        self,
        object_name: str,
        client_action: str = "get_object",
        expires_in: int = 3600,
    ) -> str:
        """Tạo Signed URL tạm thời để client upload/download file an toàn."""
        ...

    @abstractmethod
    async def delete_object(self, object_name: str) -> bool:
        """Xóa 1 file trong kho storage."""
        ...


class S3StorageAdapter(StoragePort):
    """
    Adapter giao tiếp với Object Storage tương thích S3 (MinIO, AWS S3...).

    Tạo Signed URL cho phép client upload/download file trực tiếp
    mà không cần đi qua API server (giảm tải băng thông).
    """

    def __init__(self) -> None:
        self.bucket = os.getenv("S3_BUCKET_NAME", "cx-feedback-imports")
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
        self.region = os.getenv("S3_REGION", "us-east-1")

    async def generate_presigned_url(
        self,
        object_name: str,
        client_action: str = "get_object",
        expires_in: int = 3600,
    ) -> str:
        """
        Tạo Signed URL tạm thời để client upload hoặc download file.

        Args:
            object_name: Tên file trong kho (ví dụ: "imports/job_abc123.csv")
            client_action: "get_object" (download) hoặc "put_object" (upload)
            expires_in: Thời gian tồn tại URL theo giây (mặc định 1 giờ)

        Returns:
            URL có chữ ký tạm thời để truy cập file
        """
        # TODO: Khi deploy thật, thay bằng boto3.client('s3').generate_presigned_url()
        # Hiện tại trả về URL mock cho môi trường local/dev
        return (
            f"{self.endpoint_url}/{self.bucket}/{object_name}"
            f"?X-Amz-Action={client_action}"
            f"&X-Amz-Expires={expires_in}"
        )

    async def delete_object(self, object_name: str) -> bool:
        """Xóa file trong kho S3."""
        # TODO: Khi deploy thật, thay bằng boto3.client('s3').delete_object()
        return True
