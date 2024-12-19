import asyncio

from apify import Actor
from loguru import logger as log

from src.services.collector.reviews_scraper import ReviewsScraper


async def main():
    async with Actor:
        try:
            # proxy_configuration = await Actor.create_proxy_configuration()
            # proxy_url = await proxy_configuration.new_url()

            log.info("Processing request...")
            scraper = ReviewsScraper(proxy_url=None)
            result = await scraper.scrape_data_with_reviews(
                url_path="/Hotel_Review-g293922-d15122569-Reviews-Dalat_Wonder_Resort-Da_Lat_Lam_Dong_Province.html",
            )

            await Actor.push_data(result.model_dump())
            log.info("Scraping process completed successfully.")
        except Exception as e:
            log.error("An error occurred during the scraping process: %s", str(e))
            raise


asyncio.run(main())
