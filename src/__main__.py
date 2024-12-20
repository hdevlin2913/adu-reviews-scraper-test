import asyncio

from apify import Actor
from loguru import logger as log

from src.presentation.request_handler import handle_request


async def main() -> None:
    async with Actor:
        try:
            log.info("Fetching input data...")
            input_data = await Actor.get_input() or {}

            log.info("Processing request...")
            await handle_request(input_data=input_data)

            log.info("Scraping process completed successfully.")
        except Exception as e:
            log.error(f"An error occurred during the scraping process: {e}")
            raise


asyncio.run(main())
