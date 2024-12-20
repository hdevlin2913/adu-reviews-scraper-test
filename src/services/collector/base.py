import asyncio
from typing import Any, Optional, Union

from aiohttp import ClientError, ClientResponse, ClientSession
from apify import Actor
from loguru import logger as log

from src.utils.headers import get_headers


class ReviewsBaseScraper:
    def __init__(self, use_apify_proxies: bool) -> None:
        self.use_apify_proxies = use_apify_proxies

    async def get_proxy_url(self) -> str | None:
        if self.use_apify_proxies:
            proxy_configuration = await Actor.create_proxy_configuration()
            proxy_url = await proxy_configuration.new_url()
            log.info(f"Using proxy: {proxy_url}")
            return proxy_url
        return None

    async def get_data(
        self,
        url: str,
        type: Optional[str] = None,
        retries: Optional[int] = 3,
    ) -> Union[ClientResponse, dict, str, Any, None]:
        attempts = 0
        proxy_url = await self.get_proxy_url()
        params = {"proxy": proxy_url} if proxy_url else {}
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
    ) -> dict:
        attempts = 0
        proxy_url = await self.get_proxy_url()
        params = {"proxy": proxy_url} if proxy_url else {}
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
                        log.error("Failed to parse response as JSON. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)

        log.error(f"Failed to post data to {url} after {retries} attempts.")
        return {}

    def generate_pagination_urls(
        self,
        base_url: str,
        page_size: int,
        total_pages: int,
        strategy: str = "search",
    ) -> list[str]:
        if strategy == "search":
            pagination_urls = [
                base_url.replace(f"oa{page_size}", f"oa{page_size * i}")
                for i in range(1, total_pages)
            ]
        elif strategy == "reviews":
            pagination_urls = [
                base_url.replace("-Reviews-", f"-Reviews-or{page_size * i}-")
                for i in range(1, total_pages)
            ]
        else:
            msg = f"Unknown pagination strategy: {strategy}"
            raise ValueError(msg)

        return list(dict.fromkeys(pagination_urls))
