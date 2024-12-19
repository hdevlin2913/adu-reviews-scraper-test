import asyncio
import json
import math
from typing import Any, Callable, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger as log

from src.schemas.location import LocationSchema
from src.schemas.place import PlaceSchema, Review
from src.schemas.search import SearchSchema
from src.services.collector.base import ReviewsBaseScraper
from src.utils.headers import get_headers


class ReviewsScraper(ReviewsBaseScraper):
    def __init__(self, proxy_url: str | None) -> None:
        super().__init__(proxy_url=proxy_url)

    @staticmethod
    def generate_pagination_urls(
        base_url: str,
        page_size: int,
        total_pages: int,
        strategy: str = "default",
    ) -> List[str]:
        if strategy == "default":
            pagination_urls = [base_url.replace(f"oa{page_size}", f"oa{page_size * i}") for i in range(1, total_pages)]
        elif strategy == "reviews":
            pagination_urls = [
                base_url.replace("-Reviews-", f"-Reviews-or{page_size * i}-") for i in range(1, total_pages)
            ]
        else:
            msg = f"Unknown pagination strategy: {strategy}"
            raise ValueError(msg)
        return list(dict.fromkeys(pagination_urls))

    async def scrape_location(self, query: str, limit: int = 10) -> List[LocationSchema]:
        payload = [
            {
                "variables": {
                    "request": {
                        "query": query,
                        "limit": limit,
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

        try:
            data = await self.post_data(
                url="https://www.tripadvisor.com/data/graphql/ids", headers=get_headers(), data=payload
            )

            if not data:
                log.warning(f"No location data found for query: {query}")
                return []

            results = data[0]["data"]["Typeahead_autocomplete"]["results"]
            return [LocationSchema.model_validate(result["details"]) for result in results]
        except (KeyError, IndexError) as e:
            log.error(f"Error parsing location data for query {query}: {e}")
            return []

    async def scrape_search_hotels(
        self,
        query: str,
        max_pages: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> List[SearchSchema]:
        try:
            locations = await self.scrape_location(query=query)
            if not locations:
                log.error(f"No locations found for query: {query}")
                return []

            location = locations[0]
            hotel_url = base_url + location.hotels_url

            response = await self.get_data(url=hotel_url, headers=get_headers(), type="text")
            if not response:
                log.error(f"No search results for query: {query}")
                return []

            results = self.parse_search_hotel(response=response, url=hotel_url)
            if not results:
                log.error(f"No parseable results for query: {query}")
                return []

            soup = BeautifulSoup(response, "lxml")
            page_size = len(results)
            total_text = soup.find("span", string=lambda t: t and "properties" in t).get_text()
            total_hotels = int(total_text.replace(",", "").split()[0])

            total_pages = int(math.ceil(total_hotels / page_size))
            if max_pages and max_pages < total_pages:
                total_pages = max_pages

            next_page_path = (
                soup.find("a", {"aria-label": "Next page"})["href"]
                if soup.find("a", {"aria-label": "Next page"})
                else None
            )
            next_page_url = urljoin(hotel_url, next_page_path)
            pagination_urls = self.generate_pagination_urls(
                base_url=next_page_url,
                page_size=page_size,
                total_pages=total_pages,
                strategy="default",
            )

            additional_results = await self.fetch_pagination_results(
                pagination_urls=pagination_urls,
                function=self.parse_search_hotel,
            )

            results.extend(additional_results)
            return results
        except Exception as e:
            log.error(f"Error in hotel search for query {query}: {e}")
            return []

    def parse_search_hotel(self, response: str, url: str) -> List[SearchSchema]:
        soup = BeautifulSoup(response, "lxml")
        parsed = []

        # First case: extracting from hotel-card-title
        for box in soup.select("span.listItem div[data-automation=hotel-card-title] a"):
            title = box.get_text(strip=True, separator=" ")
            href = box.get("href")
            parsed.append(SearchSchema(name=title, url=urljoin(url, href)))

        if parsed:
            return parsed

        # Fallback: extracting from listing_title
        for box in soup.select("div.listing_title > a"):
            title = box.get_text(strip=True).split(". ")[-1]
            href = box.get("href")
            parsed.append(SearchSchema(name=title, url=urljoin(url, href)))

        return parsed

    async def scrape_data_with_reviews(
        self,
        url_path: str,
        page_size: Optional[int] = 10,
        max_pages: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> PlaceSchema:
        url = base_url + url_path
        response = await self.get_data(url=url, headers=get_headers(), type="text")
        if not response:
            log.error(f"Could not scrape data for {url}")
            return {}

        results = self.parse_data_with_reviews(response=response)
        if not results:
            log.error(f"Could not parse data for {url}")
            return {}

        total_reviews = int(results.basic_data.aggregate_rating.review_count)
        total_pages = math.ceil(total_reviews / page_size)
        if max_pages and max_pages < total_pages:
            total_pages = max_pages

        pagination_urls = self.generate_pagination_urls(
            base_url=url,
            page_size=page_size,
            total_pages=total_pages,
            strategy="reviews",
        )

        additional_results = await self.fetch_pagination_results(
            pagination_urls=pagination_urls,
            function=self.parse_data_with_reviews,
        )
        for response in additional_results:
            results.reviews.extend(response["reviews"])
        return results

    def parse_data_with_reviews(self, response: str, url: Optional[str] = None) -> PlaceSchema:
        soup = BeautifulSoup(response, "lxml")
        with open(file="response.html", mode="w", encoding="utf-8") as file:
            file.write(soup.prettify(encoding="utf-8", formatter="html5").decode("utf-8"))

        # Extract basic data
        script_tag = soup.find("script", string=lambda x: x and "aggregateRating" in x)
        basic_data = json.loads(script_tag.string) if script_tag else {}

        # Extract description
        description_tag = soup.select_one("div.fIrGe._T")
        description = description_tag.get_text(strip=True) if description_tag else None

        # Extract amenities
        amenities = [feature.get_text(strip=True) for feature in soup.select("div[data-test-target*='amenity']")]

        # Extract reviews
        reviews = []
        for review in soup.select("div[data-reviewid]"):
            rate_tag = review.select_one("div[data-test-target='review-rating'] title")
            title_tag = review.select_one("div[data-test-target='review-title'] a span span")
            text_tag = review.select("span[data-automation*='reviewText'] span")
            trip_date_div = review.select_one("div.PDZqu")
            trip_date_tag = trip_date_div.find("span")

            rate = rate_tag.get_text(strip=True).split()[0].replace(",", ".") if rate_tag else None
            title = title_tag.get_text(strip=True) if title_tag else None
            text = "".join([span.get_text(strip=True) for span in text_tag]) if text_tag else None
            trip_date = (
                " ".join([word.capitalize() for word in trip_date_tag.get_text(strip=True).split(":")[-1].split()])
                if trip_date_tag
                else None
            )

            reviews.append(Review(title=title, text=text, rate=rate, trip_date=trip_date))

        return PlaceSchema(basic_data=basic_data, description=description, features=amenities, reviews=reviews)

    async def fetch_pagination_results(
        self,
        pagination_urls: List[str],
        function: Callable,
    ) -> List[Any]:
        results = []
        for url in pagination_urls:
            response = await self.get_data(url=url, headers=get_headers(), type="text")
            data = function(response=response, url=url)

            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                results.extend(data)

            await asyncio.sleep(1)

        return results
