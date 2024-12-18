import os
import shutil
from typing import Any

from loguru import logger

from scraper.core.configs.base import Settings
from scraper.infrastructure.storage.base import StorageManager


class LocalStorageManager(StorageManager):
    def __init__(self, settings: Settings) -> None:
        self._storage_directory = settings.storage_settings.local_storage_directory
        assert self._storage_directory, "Storage directory is not configured"
        if not os.path.exists(self._storage_directory):
            os.makedirs(self._storage_directory)

    def _get_local_file_path(self, file_key: str) -> str:
        assert self._storage_directory, "Storage directory is not configured"
        return os.path.join(self._storage_directory, file_key)

    def upload_file(self, file_path: str, file_key: str, content_type: str = "application/octet-stream") -> None:
        """Uploads a file to local storage."""
        dest_path = self._get_local_file_path(file_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            shutil.copy2(file_path, dest_path)
        except FileNotFoundError as e:
            logger.error(f"Error uploading file: {e}")

    def delete_files(self, file_keys: list[str]) -> None:
        """Deletes files from local storage."""
        for file_key in file_keys:
            file_path = self._get_local_file_path(file_key)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    logger.warning(f"File {file_key} does not exist")
            except OSError as e:
                logger.error(f"Error deleting file {file_key}: {e}")

    def get_file_size(self, file_key: str) -> int:
        """Gets the size of a file in local storage."""
        file_path = self._get_local_file_path(file_key)
        try:
            file_size = os.path.getsize(file_path)
            return file_size
        except FileNotFoundError:
            logger.error(f"File {file_key} not found")
            return 0

    def get_zero_byte_mp4_files(self) -> list[str]:
        """Returns a list of zero-byte .mp4 files in the local storage directory."""
        assert self._storage_directory, "Storage directory is not configured"
        zero_byte_mp4_files = []
        for root, _, files in os.walk(self._storage_directory):
            for file_name in files:
                if file_name.endswith(".mp4"):
                    file_path = os.path.join(root, file_name)
                    if os.path.getsize(file_path) == 0:
                        zero_byte_mp4_files.append(file_name)
        return zero_byte_mp4_files

    def generate_presigned_post_url(
        self,
        object_name: str,
        expiration: int,
        fields: dict[str, Any] | None = None,
        conditions: list[Any] | dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Generates a presigned post URL for local storage."""
        logger.warning("Presigned post URL generation is not supported for local storage")
        return None
