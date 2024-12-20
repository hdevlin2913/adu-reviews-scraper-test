from typing import Any

from apify import Actor
from loguru import logger as log

from src.services.collector.reviews_scraper import ReviewsScraper
from src.utils.constants import PLACE_TYPES_FUNCTION


async def handle_request(input_data: Any) -> None:
    use_apify_proxies = input_data.get("useApifyProxy", False)
    scraper = ReviewsScraper(use_apify_proxies=use_apify_proxies)


    params = input_data.get("params", {})
    places_query = params.get("query", [])

    place_type = input_data.get("type", "attractions")
    search_func, details_func = PLACE_TYPES_FUNCTION[place_type]

    for place_query in places_query:
        scrape_search_func = getattr(scraper, search_func)
        scrape_details_func = getattr(scraper, details_func)
        results = await scrape_search_func(
            query=place_query, max_places_page=params.get("max_places_page", None)
        )
        for result in results:
            log.info(f"Scraping data for {result.url}")
            place = await scrape_details_func(
                url_path=result.url, max_reviews_page=params.get("max_reviews_page", None)
            )
            if place:
                log.info("Pushing result to the dataset...")
                await Actor.push_data(place.model_dump())
