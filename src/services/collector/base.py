import asyncio
from typing import Any, Dict, Optional, Union

from aiohttp import ClientError, ClientResponse, ClientSession
from loguru import logger as log


class ReviewsBaseScraper:
    def __init__(self, proxy_url: str | None) -> None:
        self.proxy_url = proxy_url

    async def get_data(
        self,
        url: str,
        headers: Dict,
        type: Optional[str] = None,
        retries: Optional[int] = 3,
    ) -> Union[ClientResponse, Dict, str, None]:
        attempts = 0
        params = {"proxy": self.proxy_url} if self.proxy_url else {}
        async with ClientSession() as session:
            async with session.get(url=url, headers=headers, **params) as response:
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
                        log.error("Error posting data: %s. Retrying...", e)
                        attempts += 1
                        await asyncio.sleep(1)
                    except ValueError:
                        log.error("Failed to parse response as JSON. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)

        log.error("Failed to post data to %s after %d attempts.", url, retries)
        return None

    async def post_data(
        self,
        url: str,
        headers: Dict,
        data: Any,
        retries: Optional[int] = 3,
    ) -> Dict:
        attempts = 0
        params = {"proxy": self.proxy_url} if self.proxy_url else {}
        async with ClientSession() as session:
            async with session.post(
                url=url, headers=headers, json=data, **params
            ) as response:
                while attempts < retries:
                    try:
                        data = await response.json()
                        return data
                    except ClientError as e:
                        log.error("Error posting data: %s. Retrying...", e)
                        attempts += 1
                        await asyncio.sleep(1)
                    except ValueError:
                        log.error("Failed to parse response as JSON. Retrying...")
                        attempts += 1
                        await asyncio.sleep(1)

        log.error("Failed to post data to %s after %d attempts.", url, retries)
        return {}
