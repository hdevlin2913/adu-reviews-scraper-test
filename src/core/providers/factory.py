from dishka import AsyncContainer, make_async_container

from src.core.configs import Settings
from src.core.providers.configs import ConfigsProvider
from src.core.providers.connection import ConnectionsProvider
from src.core.providers.managers import ManagerProvider


def make_container(settings: Settings) -> AsyncContainer:
    container = make_async_container(
        ConfigsProvider(settings=settings),
        ConnectionsProvider(),
        ManagerProvider(),
    )
    return container
