from typing import Any

from botocore.exceptions import ClientError
from loguru import logger
from mypy_boto3_s3 import S3Client

from scraper.core.configs import Settings
from scraper.infrastructure.storage.base import StorageManager


class S3StorageManager(StorageManager):
    def __init__(self, s3_client: S3Client, settings: Settings) -> None:
        self._s3_client = s3_client
        self._bucket = settings.storage_settings.bucket

    def upload_file(self, file_path: str, file_key: str, content_type: str = "application/octet-stream") -> None:
        assert self._bucket, "Storage bucket is not configured"
        with open(file_path, "rb") as file_content:
            self._s3_client.put_object(
                Bucket=self._bucket,
                Key=file_key,
                Body=file_content,
                ACL="public-read",
                ContentType=content_type if content_type else "application/octet-stream",
                CacheControl="max-age=31536000, public",
            )

    def delete_files(self, file_keys: list[str]) -> None:
        assert self._bucket, "Storage bucket is not configured"
        self._s3_client.delete_objects(Bucket=self._bucket, Delete={"Objects": [{"Key": key} for key in file_keys]})

    def get_file_size(self, file_key: str) -> int:
        assert self._bucket, "Storage bucket is not configured"
        try:
            response = self._s3_client.head_object(Bucket=self._bucket, Key=file_key)
            file_size = response["ContentLength"]
            return file_size
        except ClientError as e:
            logger.error(f"Error retrieving file size: {e}")
            return 0

    def get_zero_byte_mp4_files(self) -> list[str]:
        zero_byte_mp4_files = []

        # Paginate through the bucket's objects
        paginator = self._s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket="zoro-asset")

        for page in pages:
            for obj in page.get("Contents", []):
                if obj["Key"].endswith(".mp4") and obj["Size"] == 0:
                    zero_byte_mp4_files.append(obj["Key"])

        return zero_byte_mp4_files

    def generate_presigned_post_url(
        self,
        object_name: str,
        expiration: int,
        fields: dict[str, Any] | None = None,
        conditions: list[Any] | dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        assert self._bucket, "Storage bucket is not configured"
        try:
            response = self._s3_client.generate_presigned_post(
                Bucket=self._bucket,
                Key=object_name,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
