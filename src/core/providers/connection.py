from typing import AsyncIterator

from boto3 import session as boto3_session
from dishka import Provider, Scope, provide
from loguru import logger as log
from mypy_boto3_s3 import S3Client
from redis.asyncio import ConnectionPool

from src.core.configs import Settings


class ConnectionsProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_pool(self, settings: Settings) -> AsyncIterator[ConnectionPool]:
        assert settings.redis_settings.url, "Redis URL is required"
        connection_pool: ConnectionPool = ConnectionPool.from_url(
            url=settings.redis_settings.url,
            max_connections=settings.redis_settings.max_connections,
        )

        yield connection_pool
        log.info("Closing Redis connection pool")
        await connection_pool.disconnect()

    @provide(scope=Scope.APP)
    async def s3_client(self, settings: Settings) -> S3Client | None:
        if (
            settings.storage_settings.access_key
            and settings.storage_settings.secret_key
        ):
            session = boto3_session.Session()
            client = session.client(
                "s3",
                region_name=settings.storage_settings.region_name,
                endpoint_url=settings.storage_settings.endpoint_url,
                aws_access_key_id=settings.storage_settings.access_key,
                aws_secret_access_key=settings.storage_settings.secret_key,
            )
            return client
        return None
