"""Object Storage adapter (S3-compatible) với interface chuẩn."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from asyncio import to_thread
from typing import Any, BinaryIO


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

    @abstractmethod
    async def download_fileobj(self, object_name: str, destination: BinaryIO) -> None:
        """Stream an object into a caller-owned seekable file object."""
        ...

    @abstractmethod
    async def upload_fileobj(
        self, object_name: str, source: BinaryIO, *, content_type: str
    ) -> None:
        """Stream a caller-owned file object into object storage."""
        ...


class S3StorageAdapter(StoragePort):
    """
    Adapter giao tiếp với Object Storage tương thích S3 (MinIO, AWS S3...).

    Tạo Signed URL cho phép client upload/download file trực tiếp
    mà không cần đi qua API server (giảm tải băng thông).
    """

    def __init__(self, client: Any | None = None) -> None:
        self.bucket = os.getenv("S3_BUCKET_NAME", "cx-feedback-imports")
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
        self.region = os.getenv("S3_REGION", "us-east-1")
        if client is None:
            import boto3

            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
        self._client = client

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
        if client_action not in {"get_object", "put_object"}:
            raise ValueError("client_action must be get_object or put_object")
        return await to_thread(
            self._client.generate_presigned_url,
            client_action,
            Params={"Bucket": self.bucket, "Key": object_name},
            ExpiresIn=expires_in,
        )

    async def delete_object(self, object_name: str) -> bool:
        """Xóa file trong kho S3."""
        await to_thread(self._client.delete_object, Bucket=self.bucket, Key=object_name)
        return True

    async def download_fileobj(self, object_name: str, destination: BinaryIO) -> None:
        """Download without materialising an import file in process memory."""
        await to_thread(
            self._client.download_fileobj,
            self.bucket,
            object_name,
            destination,
        )
        destination.seek(0)

    async def upload_fileobj(
        self, object_name: str, source: BinaryIO, *, content_type: str
    ) -> None:
        """Upload a report/original stream with an explicit content type."""
        source.seek(0)
        await to_thread(
            self._client.upload_fileobj,
            source,
            self.bucket,
            object_name,
            ExtraArgs={"ContentType": content_type},
        )
