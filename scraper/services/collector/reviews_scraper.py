import asyncio
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urljoin

from loguru import logger as log
from parsel import Selector

from scraper.schemas.location import LocationDataSchema
from scraper.schemas.search import SearchSchema
from scraper.services.collector.base import ReviewsBaseScraper
from scraper.utils.headers import get_headers


class ReviewsScraper(ReviewsBaseScraper):
    @staticmethod
    def generate_pagination_urls(
        base_url: str, page_size: int, total_pages: int, strategy: str = "default"
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

    async def get_location(self, query: str, limit: int = 10) -> List[LocationDataSchema]:
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

        headers = get_headers()
        headers.update({"Referer": "https://www.tripadvisor.com/Hotels"})

        try:
            data = await self.post_data(
                url="https://www.tripadvisor.com/data/graphql/ids", headers=headers, data=payload
            )

            if not data:
                log.warning(f"No location data found for query: {query}")
                return []

            results = data[0]["data"]["Typeahead_autocomplete"]["results"]
            return [LocationDataSchema.model_validate(result["details"]) for result in results]
        except (KeyError, IndexError) as e:
            log.error(f"Error parsing location data for query {query}: {e}")
            return []

    async def scrape_search_hotels(
        self, query: str, max_pages: Optional[int] = None, base_url: str = "https://www.tripadvisor.com"
    ) -> List[SearchSchema]:
        try:
            locations = await self.get_location(query=query)
            if not locations:
                log.error(f"No locations found for query: {query}")
                return []

            location = locations[0]
            hotel_url = base_url + location.hotels_url

            response = await self.get_data(url=hotel_url, headers=get_headers(), type="text")
            if not response:
                log.error(f"No search results for query: {query}")
                return []

            results = await self.parse_search_hotel(response=response, url=hotel_url)
            if not results:
                log.error(f"No parseable results for query: {query}")
                return []

            selector = Selector(response)
            page_size = len(results)
            total_text = selector.xpath("//span/text()").re(r"(\d*\,*\d+) properties")[0]
            total_hotels = int(total_text.replace(",", ""))

            total_pages = int(math.ceil(total_hotels / page_size))
            if max_pages and max_pages < total_pages:
                total_pages = max_pages

            next_page_path = selector.css('a[aria-label="Next page"]::attr(href)').get()
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

    async def parse_search_hotel(self, response: str, url: str) -> List[SearchSchema]:
        selector = Selector(response)
        parsed = []

        for box in selector.css("span.listItem"):
            title = box.css("div[data-automation=hotel-card-title] a ::text").getall()[1]
            url = box.css("div[data-automation=hotel-card-title] a::attr(href)").get()
            parsed.append(SearchSchema(name=title, url=urljoin(str(url), url)))

        if parsed:
            return parsed

        for box in selector.css("div.listing_title>a"):
            parsed.append(
                SearchSchema(
                    name=box.xpath("text()").get("").split(". ")[-1],
                    url=urljoin(str(url), box.xpath("@href").get()),
                )
            )
        return parsed

    async def scrape_data_with_reviews(
        self,
        url_path: str,
        page_size: Optional[int] = 10,
        max_pages: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> Dict:
        url = base_url + url_path
        response = await self.get_data(url=url, headers=get_headers(), type="text")
        if not response:
            log.error(f"Could not scrape data for {url}")
            return {}

        results = await self.parse_data_with_reviews(response=response)
        if not results:
            log.error(f"Could not parse data for {url}")
            return {}

        total_reviews = int(results["basic_data"]["aggregateRating"]["reviewCount"])
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
            results["reviews"].extend(response["reviews"])
        return results

    async def parse_data_with_reviews(self, response: str, url: Optional[str] = None) -> Dict:
        selector = Selector(response)
        basic_data = json.loads(selector.xpath("//script[contains(text(),'aggregateRating')]/text()").get())
        description = selector.css("div.fIrGe._T::text").get()

        amenities = []
        for feature in selector.xpath("//div[contains(@data-test-target, 'amenity')]/text()"):
            amenities.append(feature.get())

        reviews = []
        for review in selector.xpath("//div[@data-reviewid]"):
            title = review.xpath(".//div[@data-test-target='review-title']/a/span/span/text()").get()
            text = "".join(review.xpath(".//span[contains(@data-automation, 'reviewText')]/span/text()").extract())
            rate_text = review.xpath(".//div[@data-test-target='review-rating']/span/@class").get()
            rate = (int(rate_text.split("ui_bubble_rating")[-1].split("_")[-1].replace("0", ""))) if rate_text else None
            trip_data = review.xpath(".//span[span[contains(text(),'Date of stay')]]/text()").get()
            reviews.append({"title": title, "text": text, "rate": rate, "tripDate": trip_data})

        return {"basic_data": basic_data, "description": description, "featues": amenities, "reviews": reviews}

    async def fetch_pagination_results(
        self,
        pagination_urls: List[str],
        function: Callable,
    ) -> List[Any]:
        results = []
        for url in pagination_urls:
            response = await self.get_data(url=url, headers=get_headers(), type="text")
            data = await function(response=response, url=url)

            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                results.extend(data)

            await asyncio.sleep(1)

        return results


if __name__ == "__main__":
    storage_dir = Path(__file__).parent.parent.parent.parent / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    scraper = ReviewsScraper()

    query_location = "Da Lat"
    results_location = asyncio.run(scraper.get_location(query=query_location))
    file_path_location = storage_dir / f"location_{query_location}.json"
    with open(file_path_location, "w", encoding="utf-8") as file:
        json.dump([item.model_dump() for item in results_location], file, ensure_ascii=False, indent=4)

    #  query_hotels = "Da Lat"
    #  results_hotels = asyncio.run(scraper.scrape_search_hotels(query=query_hotels, max_pages=2))
    #  file_path_hotels = storage_dir / f"search_hotels_{query_hotels}.json"
    #  with open(file_path_hotels, "w", encoding="utf-8") as file:
    #      json.dump([item.model_dump() for item in results_hotels], file, ensure_ascii=False, indent=4)

    #  for item in results_hotels:
    #      hotel_data = asyncio.run(scraper.scrape_data_with_reviews(url_path=item.url))
    #      file_path_hotel = storage_dir / f"result_hotel_{item.name}.json"
    #      with open(file_path_hotel, "w", encoding="utf-8") as file:
    #          json.dump(hotel_data, file, ensure_ascii=False, indent=4)
