from scraper import config
from db import gino_db
import asyncio
from scraper.utils.data.load_dicitionary_to_redis import load_data
from scraper.utils.data.seed_redis_with_pages import load_redis_data
import logging
from scraper.scraper import get_multiple_pages
import time
from db.models import Domain
from os import getcwd, path

from utils.data.gino_utils import get_list_of_domains, init_db


async def main(loop):
    start = time.perf_counter()
    await init_db()
    await load_data()
    list_of_domains = await get_list_of_domains()
    # TODO: mark them as gotten
    await load_redis_data(list_of_domains)
    await get_multiple_pages(loop)
    duration = time.perf_counter() - start
    print(f'Crawled {len(list_of_domains)} domains in {duration}')


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, filename='scraper/app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

    # loop = asyncio.get_event_loop()
    # print('about to init the db')
    # loop.run_until_complete(init_db())
    # print('about to load data')
    # loop.run_until_complete(load_data())
    # list_of_domains = loop.run_until_complete(get_list_of_domains())
    # loop.run_until_complete(load_redis_data(list_of_domains))
    # loop.run_until_complete(get_multiple_pages(loop))
