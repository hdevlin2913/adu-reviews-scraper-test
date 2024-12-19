from abc import ABC, abstractmethod
from typing import Any


class StorageManager(ABC):
    @abstractmethod
    def upload_file(self, file_path: str, file_key: str, content_type: str) -> None:
        pass

    @abstractmethod
    def delete_files(self, file_keys: list[str]) -> None:
        pass

    @abstractmethod
    def get_file_size(self, file_key: str) -> int:
        pass

    @abstractmethod
    def get_zero_byte_mp4_files(self) -> list[str]:
        pass

    @abstractmethod
    def generate_presigned_post_url(
        self,
        object_name: str,
        expiration: int,
        fields: dict[str, Any] | None = None,
        conditions: list[Any] | dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        pass
