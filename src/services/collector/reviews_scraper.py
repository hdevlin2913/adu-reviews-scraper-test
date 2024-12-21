import asyncio
import json
import math
from typing import Any, Callable, Optional, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger as log

from src.schemas.collector.location import LocationSchema
from src.schemas.collector.place import PlaceSchema, ReviewSchema
from src.schemas.collector.search import SearchSchema
from src.services.collector.base import ReviewsBaseScraper


class ReviewsScraper(ReviewsBaseScraper):
    def __init__(self, use_apify_proxies: bool) -> None:
        super().__init__(use_apify_proxies=use_apify_proxies)

    async def fetch_pagination_results(
        self,
        base_url: str,
        page_size: int,
        total_pages: int,
        strategy: str,
        parse_function: Callable,
    ) -> list[Any]:
        pagination_urls = self.generate_pagination_urls(
            base_url=base_url,
            page_size=page_size,
            total_pages=total_pages,
            strategy=strategy,
        )

        results = []
        for url in pagination_urls:
            try:
                response = await self.get_data(url=url, type="text")
                data = parse_function(response=response)

                if isinstance(data, list):
                    results.extend(data)
                else:
                    results.append(data)

                await asyncio.sleep(5)
            except Exception as e:
                log.error(f"Error in fetching pagination results for {url}: {e}")

        return results

    async def scrape_location(
        self,
        query: str,
        limit: int = 10,
    ) -> list[LocationSchema]:
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
                url="https://www.tripadvisor.com/data/graphql/ids", data=payload
            )

            if not data:
                log.warning(f"No location data found for query: {query}")
                return []

            results = data[0]["data"]["Typeahead_autocomplete"]["results"]
            return [
                LocationSchema.model_validate(result["details"]) for result in results
            ]
        except Exception as e:
            log.error(f"Error in location search for query {query}: {e}")
            return []

    async def scrape_search_attractions(
        self,
        query: str,
        max_places_page: Optional[int] = None,
        max_reviews_page: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> list[SearchSchema]:
        try:
            locations = await self.scrape_location(query=query)
            if not locations:
                log.error(f"No locations found for query: {query}")
                return []

            location = locations[0]
            if location.is_geo is False:
                return await self.scrape_attraction_details(
                    url_path=location.url, max_reviews_page=max_reviews_page
                )

            attractions_url = base_url + location.attractions_url.replace(
                "-Activities-", "-Activities-oa0-"
            )

            log.info(f"Scraping attractions for query: {query}")

            response = await self.get_data(url=attractions_url, type="text")
            if not response:
                log.error(f"No search results for query: {query}")
                return []

            results = self.parse_search_attractions(response=response)
            if not results:
                log.error(f"No parseable results for query: {query}")
                return []

            soup = BeautifulSoup(response, "lxml")
            attractions_page_size = len(results)
            total_tag = soup.find(
                "section", {"data-automation": "WebPresentation_WebSortDisclaimer"}
            )
            total_attractions = int(total_tag.get_text().split(" ")[0])

            total_attractions_pages = int(
                math.ceil(total_attractions / attractions_page_size)
            )
            if max_places_page and max_places_page < total_attractions_pages:
                total_attractions_pages = max_places_page

            next_page_tag = soup.find("a", {"aria-label": "Next page"})["href"]
            next_page_url = urljoin(attractions_url, next_page_tag)

            additional_results = await self.fetch_pagination_results(
                base_url=next_page_url,
                page_size=attractions_page_size,
                total_pages=total_attractions_pages,
                strategy="search",
                parse_function=self.parse_search_attractions,
            )

            results.extend(additional_results)

            log.info(f"Scraped {len(results)} attractions for query: {query}")

            return results
        except Exception as e:
            log.error(f"Error in search attractions for query {query}: {e}")
            return []

    def parse_search_attractions(
        self,
        response: str,
    ) -> list[SearchSchema]:
        soup = BeautifulSoup(response, "lxml")
        parsed = []

        card_sections = soup.select(
            "section.mowmC[data-automation='WebPresentation_SingleFlexCardSection'] header.VLKGO a:first-of-type"
        )
        for box in card_sections:
            title = box.get_text(strip=True, separator=" ")
            href = box.get("href")
            parsed.append(SearchSchema(name=title, url=href))

        return parsed

    async def scrape_attraction_details(
        self,
        url_path: str,
        max_reviews_page: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> PlaceSchema | None:
        try:
            url = base_url + url_path
            response = await self.get_data(url=url, type="text")
            if not response:
                log.error(f"No attraction details found for {url}")
                return None

            attraction_details = self.parse_attraction_details(response=response)
            if not attraction_details:
                log.error(f"No parseable attraction details found for {url}")
                return None

            log.info(
                f"Scraping attraction details for {attraction_details.basic_data.name}"
            )

            reviews_page_size = len(attraction_details.reviews) or 0
            if reviews_page_size == 0:
                return attraction_details

            total_reviews = int(
                attraction_details.basic_data.aggregate_rating.review_count
            )
            total_reviews_pages = math.ceil(total_reviews / reviews_page_size)
            if max_reviews_page and max_reviews_page < total_reviews_pages:
                total_reviews_pages = max_reviews_page

            additional_results = await self.fetch_pagination_results(
                base_url=url,
                page_size=reviews_page_size,
                total_pages=total_reviews_pages,
                strategy="reviews",
                parse_function=self.parse_attraction_details,
            )

            attraction_details.reviews.extend(
                getattr(response, "reviews", []) for response in additional_results
            )

            log.info(
                f"Scraped {len(attraction_details.reviews)} reviews for {attraction_details.basic_data.name}"
            )

            return attraction_details
        except Exception as e:
            log.error(
                f"Error in scraping attraction details with reviews for {url}: {e}"
            )
            return None

    def parse_attraction_details(
        self,
        response: str,
    ) -> PlaceSchema | None:
        try:
            soup = BeautifulSoup(response, "lxml")

            script_tag = soup.find(
                "script", string=lambda x: x and "aggregateRating" in x
            )
            basic_data = json.loads(script_tag.string) if script_tag else {}

            description_tag = soup.select_one("div.fIrGe._T")
            description = (
                description_tag.get_text(strip=True) if description_tag else None
            )

            reviews = []
            for review in soup.select("div[data-automation='reviewCard']"):
                rate_tag = review.select_one('title[id*="lithium"]')
                title_tag = review.select_one("a[href*='/ShowUserReviews']")
                text_tag = review.select("div.fIrGe._T")
                trip_date_tag = review.select_one("div.RpeCd")

                rate = (
                    rate_tag.get_text(strip=True).split()[0].replace(",", ".")
                    if rate_tag
                    else None
                )
                title = title_tag.get_text(strip=True) if title_tag else None
                text = (
                    "".join([span.get_text(strip=True) for span in text_tag])
                    if text_tag
                    else None
                )
                trip_date = (
                    trip_date_tag.get_text(strip=True).split("•")[0]
                    if trip_date_tag
                    else None
                )

                reviews.append(
                    ReviewSchema(title=title, text=text, rate=rate, trip_date=trip_date)
                )

            return PlaceSchema(
                basic_data=basic_data,
                description=description,
                reviews=reviews,
            )
        except Exception as e:
            log.error(f"Error in parsing attraction details with reviews: {e}")
            return None

    async def scrape_search_hotels(
        self,
        query: str,
        max_places_page: Optional[int] = None,
        max_reviews_page: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> Union[list[SearchSchema], PlaceSchema, None]:
        try:
            locations = await self.scrape_location(query=query)
            if not locations:
                log.error(f"No locations found for query: {query}")
                return []

            location = locations[0]
            if location.is_geo is False:
                return await self.scrape_hotel_details(
                    url_path=location.url, max_reviews_page=max_reviews_page
                )

            hotel_url = base_url + location.hotels_url

            log.info(f"Scraping hotels for query: {query}")

            response = await self.get_data(url=hotel_url, type="text")
            if not response:
                log.error(f"No search results for query: {query}")
                return []

            results = self.parse_search_hotel(response=response)
            if not results:
                log.error(f"No parseable results for query: {query}")
                return []

            soup = BeautifulSoup(response, "lxml")
            hotels_page_size = len(results)
            total_tag = soup.find("span", string=lambda t: t and "properties" in t)
            total_hotels = int(total_tag.get_text().replace(",", "").split()[0])

            total_hotels_pages = int(math.ceil(total_hotels / hotels_page_size))
            if max_places_page and max_places_page < total_hotels_pages:
                total_hotels_pages = max_places_page

            next_page_tag = soup.find("a", {"aria-label": "Next page"})["href"]
            next_page_url = urljoin(hotel_url, next_page_tag)

            additional_results = await self.fetch_pagination_results(
                base_url=next_page_url,
                page_size=hotels_page_size,
                total_pages=total_hotels_pages,
                strategy="search",
                parse_function=self.parse_search_hotel,
            )

            results.extend(additional_results)

            log.info(f"Scraped {len(results)} hotels for query: {query}")

            return results
        except Exception as e:
            log.error(f"Error in search hotels for query {query}: {e}")
            return []

    def parse_search_hotel(
        self,
        response: str,
    ) -> list[SearchSchema]:
        soup = BeautifulSoup(response, "lxml")
        parsed = []

        for box in soup.select("span.listItem div[data-automation=hotel-card-title] a"):
            title = box.get_text(strip=True, separator=" ")
            href = box.get("href")
            parsed.append(SearchSchema(name=title, url=href))

        if parsed:
            return parsed

        for box in soup.select("div.listing_title > a"):
            title = box.get_text(strip=True).split(". ")[-1]
            href = box.get("href")
            parsed.append(SearchSchema(name=title, url=href))

        return parsed

    async def scrape_hotel_details(
        self,
        url_path: str,
        max_reviews_page: Optional[int] = None,
        base_url: str = "https://www.tripadvisor.com",
    ) -> PlaceSchema | None:
        try:
            url = base_url + url_path
            result = await self.get_data(url=url, type="text")
            if not result:
                log.error(f"No hotel details found for {url}")
                return None

            hotel_details = self.parse_hotel_details(response=result)
            if not hotel_details:
                log.error(f"No parseable hotel details found for {url}")
                return None

            log.info(f"Scraping hotel details for {hotel_details.basic_data.name}")

            reviews_page_size = len(hotel_details.reviews) or 0
            if reviews_page_size == 0:
                return hotel_details

            total_reviews = int(hotel_details.basic_data.aggregate_rating.review_count)
            total_reviews_pages = math.ceil(total_reviews / reviews_page_size)
            if max_reviews_page and max_reviews_page < total_reviews_pages:
                total_reviews_pages = max_reviews_page

            additional_results = await self.fetch_pagination_results(
                base_url=url,
                page_size=reviews_page_size,
                total_pages=total_reviews_pages,
                strategy="reviews",
                parse_function=self.parse_hotel_details,
            )

            hotel_details.reviews.extend(
                getattr(result, "reviews", []) for result in additional_results
            )

            log.info(
                f"Scraped {len(hotel_details.reviews)} reviews for {hotel_details.basic_data.name}"
            )

            return hotel_details
        except Exception as e:
            log.error(f"Error in scraping hotel details with reviews for {url}: {e}")
            return None

    def parse_hotel_details(
        self,
        response: str,
    ) -> PlaceSchema | None:
        try:
            soup = BeautifulSoup(response, "lxml")

            script_tag = soup.find(
                "script", string=lambda x: x and "aggregateRating" in x
            )
            basic_data = json.loads(script_tag.string) if script_tag else {}

            description_tag = soup.select_one("div.fIrGe._T")
            description = (
                description_tag.get_text(strip=True) if description_tag else None
            )

            amenities = [
                feature.get_text(strip=True)
                for feature in soup.select("div[data-test-target*='amenity']")
            ]

            reviews = []
            for review in soup.select("div[data-reviewid]"):
                rate_tag = review.select_one(
                    "div[data-test-target='review-rating'] title"
                )
                title_tag = review.select_one(
                    "div[data-test-target='review-title'] a span span"
                )
                text_tag = review.select("span[data-automation*='reviewText'] span")
                trip_date_div = review.select_one("div.PDZqu")
                trip_date_tag = trip_date_div.find("span")

                rate = (
                    rate_tag.get_text(strip=True).split()[0].replace(",", ".")
                    if rate_tag
                    else None
                )
                title = title_tag.get_text(strip=True) if title_tag else None
                text = (
                    "".join([span.get_text(strip=True) for span in text_tag])
                    if text_tag
                    else None
                )
                trip_date = (
                    " ".join(
                        [
                            word.capitalize()
                            for word in trip_date_tag.get_text(strip=True)
                            .split(":")[-1]
                            .split()
                        ]
                    )
                    if trip_date_tag
                    else None
                )

                reviews.append(
                    ReviewSchema(title=title, text=text, rate=rate, trip_date=trip_date)
                )

            return PlaceSchema(
                basic_data=basic_data,
                description=description,
                features=amenities,
                reviews=reviews,
            )
        except Exception as e:
            log.error(f"Error in parsing hotel details with reviews: {e}")
            return None
