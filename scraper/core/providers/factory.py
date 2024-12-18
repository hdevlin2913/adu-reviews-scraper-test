from dishka import AsyncContainer, make_async_container

from scraper.core.configs import Settings
from scraper.core.providers.configs import ConfigsProvider
from scraper.core.providers.connection import ConnectionsProvider
from scraper.core.providers.managers import ManagerProvider


def make_container(settings: Settings) -> AsyncContainer:
    container = make_async_container(
        ConfigsProvider(settings=settings),
        ConnectionsProvider(),
        ManagerProvider(),
    )
    return container
