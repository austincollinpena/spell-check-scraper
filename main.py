from scraper import config
from db import db
import asyncio
from scraper.utils.data.load_dicitionary_to_redis import load_data
from scraper.utils.data.seed_redis_with_pages import load_redis_data
import logging
from scraper.scraper import get_multiple_pages
import time
from db.models import Domain
from os import getcwd, path

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, filename='scraper/app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    db.set_bind(config.DB_DSN, echo=True)
    start = time.perf_counter()
    # Load the english dicitionary. Pass through override=True to force reload after the first run
    asyncio.run(load_data())
    # TODO: Get the domains and mark them as gotten
    # Add the domains to Redis (will add from db in future)
    list_of_domains = db.all(Domain.query)
    asyncio.run(load_redis_data(list_of_domains))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_multiple_pages(loop))
    duration = time.perf_counter() - start
    print(f'Crawled {len(list_of_domains)} domains in {duration}')
