import os
from functools import lru_cache

from src.core.configs.base import Settings
from src.core.configs.dev import DevSettings
from src.core.configs.prod import ProdSettings


@lru_cache
def get_settings() -> Settings:
    config_env = os.environ.get("CONFIG_ENV", "dev")

    if config_env == "dev":
        return DevSettings()

    if config_env == "prod":
        return ProdSettings()

    return Settings()


settings = get_settings()

__all__ = ["settings", "Settings", "get_settings"]
