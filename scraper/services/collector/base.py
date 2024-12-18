import asyncio
from typing import Any, Dict, Optional, Union

from aiohttp import ClientError, ClientResponse, ClientSession
from loguru import logger as log


class ReviewsBaseScraper:
    async def get_data(
        self, url: str, headers: Dict, type: Optional[str] = None, retries: Optional[int] = 3
    ) -> Union[ClientResponse, Dict, str, None]:
        payload = [
            {
                "variables": {
                    "request": {
                        "scope": "WORLDWIDE",
                        "locale": "vi",
                        "scopeGeoId": 1,
                        "searchCenter": None,
                        # Note: Can expand to search for differents.
                        "types": [
                            "LOCATION",
                            # "QUERY_SUGGESTION",
                            # "RESCUE_RESULT"
                        ],
                        "locationTypes": [
                            "GEO",
                            "AIRPORT",
                            "ACCOMMODATION",
                            "ATTRACTION",
                            "ATTRACTION_PRODUCT",
                            "EATERY",
                            "NEIGHBORHOOD",
                            "AIRLINE",
                            "SHOPPING",
                            "UNIVERSITY",
                            "GENERAL_HOSPITAL",
                            "PORT",
                            "FERRY",
                            "CORPORATION",
                            "VACATION_RENTAL",
                            "SHIP",
                            "CRUISE_LINE",
                            "CAR_RENTAL_OFFICE",
                        ],
                        "userId": None,
                        "context": {},
                        "enabledFeatures": ["articles"],
                        "includeRecent": True,
                    }
                },
                "query": "84b17ed122fbdbd4",
                "extensions": {"preRegisteredQueryId": "84b17ed122fbdbd4"},
            }
        ]

        attempts = 0
        async with ClientSession() as session:
            async with session.get(url=url, headers=headers, json=payload) as response:
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

    async def post_data(self, url: str, headers: Dict, data: Any, retries: Optional[int] = 3) -> Dict:
        attempts = 0
        async with ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
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
