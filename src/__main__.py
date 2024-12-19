import asyncio

from apify import Actor
from loguru import logger as log

from src.services.collector.reviews_scraper import ReviewsScraper


async def main():
    async with Actor:
        try:
            proxy_configuration = await Actor.create_proxy_configuration()
            proxy_url = await proxy_configuration.new_url()

            scraper = ReviewsScraper(proxy_url=proxy_url)
            result = await scraper.scrape_data_with_reviews(
                url_path="/Hotel_Review-g293922-d299557-Reviews-Dalat_Palace_Heritage_Hotel-Da_Lat_Lam_Dong_Province.html",
            )

            log.info(f"Pushing {len(result)} results to the dataset...")
            await Actor.push_data(result)
            log.info("Scraping process completed successfully.")
        except Exception as e:
            log.error("An error occurred during the scraping process: %s", str(e))
            raise


asyncio.run(main())
