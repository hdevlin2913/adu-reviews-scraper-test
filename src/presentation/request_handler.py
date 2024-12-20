from typing import Any, List

from apify import Actor
from loguru import logger as log

from src.schemas.collector.place import PlaceSchema
from src.services.collector.reviews_scraper import ReviewsScraper


async def handle_request(input_data: Any) -> List[PlaceSchema]:
    use_apify_proxies = input_data.get("useApifyProxy", False)

    scraper = ReviewsScraper(use_apify_proxies=use_apify_proxies)

    responses = []
    places_query = input_data.get("query", [])
    for place_query in places_query:
        results = await scraper.scrape_search_attractions(query=place_query, max_pages=1)
        for result in results:
            log.info(f"Scraping data for {result.url}")
            place = await scraper.scrape_attraction_details(url_path=result.url, max_pages=1)
            if place:
                log.info("Pushing result to the dataset...")
                responses.append(place)
                await Actor.push_data(place.model_dump())

    return responses
