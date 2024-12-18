import asyncio
from typing import Any, Dict, Optional, Union

from aiohttp import BasicAuth, ClientError, ClientResponse, ClientSession
from apify import Actor
from loguru import logger as log

from src.utils.headers import get_headers


class ReviewsBaseScraper:
    def __init__(self, use_apify_proxies: bool) -> None:
        self.use_apify_proxies = use_apify_proxies

    async def get_proxy_url(self) -> Optional[tuple[str, str, str]]:
        if self.use_apify_proxies:
            proxy_configuration = await Actor.create_proxy_configuration(
                groups=["RESIDENTIAL"]
            )
            proxy_url = await proxy_configuration.new_url()
            username = proxy_configuration._get_username()
            password = proxy_configuration._password
            log.info(f"Using proxy: {proxy_url}")
            return proxy_url, username, password
        return None

    async def get_data(
        self,
        url: str,
        type: Optional[str] = None,
        retries: Optional[int] = 3,
    ) -> Union[ClientResponse, Dict, str, None]:
        attempts = 0
        proxy_data = await self.get_proxy_url()
        params = (
            {
                "proxy": proxy_data[0],
                "proxy_auth": BasicAuth(login=proxy_data[1], password=proxy_data[2]),
            }
            if proxy_data
            else {}
        )
        async with ClientSession() as session:
            async with session.get(
                url=url, headers=get_headers(), **params
            ) as response:
                while attempts < retries:
                    try:
                        if type == "json":
                            data = await response.json()
                            return data

                        if type == "text":
                            data = await response.text(encoding="utf-8")
                            return data

                        return response
                    except ClientError as e:
                        log.error(f"Error posting data: {e}. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)
                    except ValueError:
                        log.error("Failed to parse response as JSON. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)

        log.error(f"Failed to post data to {url} after {retries} attempts.")
        return None

    async def post_data(
        self,
        url: str,
        data: Any,
        retries: Optional[int] = 3,
    ) -> Dict:
        attempts = 0
        proxy_data = await self.get_proxy_url()
        params = (
            {
                "proxy": proxy_data[0],
                "proxy_auth": BasicAuth(login=proxy_data[1], password=proxy_data[2]),
            }
            if proxy_data
            else {}
        )
        async with ClientSession() as session:
            async with session.post(
                url=url, headers=get_headers(), json=data, **params
            ) as response:
                while attempts < retries:
                    try:
                        data = await response.json()
                        return data
                    except ClientError as e:
                        log.error(f"Error posting data: {e}. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)
                    except ValueError:
                        log.error(f"Failed to parse response as JSON. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)

        log.error(f"Failed to post data to {url} after {retries} attempts.")
        return {}
