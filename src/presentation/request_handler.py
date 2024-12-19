from typing import Any, List

from apify import Actor
from loguru import logger as log

from src.schemas.place import PlaceSchema
from src.services.collector.reviews_scraper import ReviewsScraper


async def handle_request(input_data: Any) -> List[PlaceSchema]:
    use_apify_proxies = input_data.get("useApifyProxy", False)

    scraper = ReviewsScraper(use_apify_proxies=use_apify_proxies)

    responses = []
    places_query = input_data.get("placesQuery", [])
    for place_query in places_query:
        hotels = await scraper.scrape_search_hotels(query=place_query, max_pages=2)
        for hotel in hotels:
            log.info(f"Scraping data for {hotel.name}")
            place = await scraper.scrape_data_with_reviews(url_path=hotel.url, max_pages=2)
            if place:
                log.info("Pushing result to the dataset...")
                responses.append(place)
                await Actor.push_data(place.model_dump())

    return responses
