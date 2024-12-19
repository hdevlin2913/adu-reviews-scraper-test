import os
from pathlib import Path
from typing import Tuple, Type

from pydantic import Field, model_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class RedisSettings(BaseSettings):
    url: str | None = None
    cache_url: str | None = None
    max_connections: int | None = 5

    @model_validator(mode="after")
    def assemble_redis_cache(self) -> "RedisSettings":
        if not self.cache_url:
            self.cache_url = self.url

        return self


class StorageSettings(BaseSettings):
    region_name: str = "sgp1"
    endpoint_url: str | None = None
    access_key: str | None = None
    secret_key: str | None = None
    bucket: str | None = None

    local_storage_directory: str | None = "storage"

    @model_validator(mode="after")
    def assemble_storage_fields(self) -> "StorageSettings":
        if self.region_name:
            self.endpoint_url = f"https://{self.region_name}.digitaloceanspaces.com"

        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    config_env: str | None = "prod"

    redis_settings: RedisSettings = Field(
        default_factory=RedisSettings, validation_alias="redis"
    )
    storage_settings: StorageSettings = Field(
        default_factory=StorageSettings, validation_alias="storage"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        config_env = os.environ.get("CONFIG_ENV", "dev")
        toml_file = Path("config").resolve() / f"{config_env}_config.toml"

        source = [
            init_settings,
            EnvSettingsSource(settings_cls),
            DotEnvSettingsSource(settings_cls, ".env"),
            TomlConfigSettingsSource(settings_cls, toml_file),
            file_secret_settings,
        ]

        return (*source,)
