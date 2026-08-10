import hashlib
import os
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

from cx_contracts.import_pkg.csv_v1 import MAX_FILE_SIZE_BYTES


class SourceFileStore:
    def __init__(self, base_dir: str = ".storage/imports"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, upload_file: UploadFile) -> tuple[str, str, int]:
        """Stream upload file to storage, calculating SHA256 and enforcing max size.
        
        Returns (storage_key, file_sha256_hex, total_bytes).
        """
        file_id = str(uuid4())
        safe_key = f"{file_id}.csv"
        file_path = self.base_dir / safe_key

        hasher = hashlib.sha256()
        total_bytes = 0

        try:
            with open(file_path, "wb") as f:
                while chunk := await upload_file.read(8192):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE_BYTES:
                        raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes")
                    hasher.hexdigest()
                    hasher.update(chunk)
                    f.write(chunk)
            
            sha256_hex = hasher.hexdigest()
            return safe_key, sha256_hex, total_bytes

        except Exception:
            if file_path.exists():
                file_path.unlink()
            raise

    def get_file_path(self, storage_key: str) -> Path:
        """Get absolute path for a storage key, preventing path traversal."""
        clean_key = Path(storage_key).name
        file_path = self.base_dir / clean_key
        if not file_path.exists():
            raise FileNotFoundError(f"Storage key not found: {storage_key}")
        return file_path

    def delete_file(self, storage_key: str) -> None:
        """Remove file from storage."""
        try:
            file_path = self.get_file_path(storage_key)
            if file_path.exists():
                file_path.unlink()
        except FileNotFoundError:
            pass
