from typing import Optional

from dishka import Provider, Scope, provide
from mypy_boto3_s3 import S3Client

from src.core.configs import Settings
from src.infrastructure.storage.base import StorageManager
from src.infrastructure.storage.local_storage import LocalStorageManager
from src.infrastructure.storage.s3_storage import S3StorageManager


class ManagerProvider(Provider):
    @provide(scope=Scope.APP)
    def storage_manager(self, settings: Settings, s3_client: Optional[S3Client]) -> StorageManager:
        if settings.config_env == "prod" and s3_client:
            return S3StorageManager(s3_client=s3_client, settings=settings)
        return LocalStorageManager(settings=settings)
