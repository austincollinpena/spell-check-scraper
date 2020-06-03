import aiohttp
import aioredis
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fake_headers import Headers

# Module Imports
from utils.scraping.get_text import get_text
from utils.scraping.extract_local_links import extract_and_queue_local_links
from utils.scraping.check_if_spelled_right import check_if_spelled_right
from db.models import Domain, Page
from db import gino_db
from utils.scraping.random_proxy import random_proxy
from scraper import config
import logging


async def parse_page(redis, url: str, session) -> None:
    header = Headers()

    async with session.get(url, headers=header.generate(), ssl=False, allow_redirects=True,
                           proxy=random_proxy()) as resp:
        current_netloc = urlparse(url).netloc
        # Get the url's parent
        try:
            domain = await Domain.query.where(Domain.domain == f'http://{current_netloc}').gino.first()
        except Exception as e:
            logging.error(f'Failed at finding {current_netloc}', exc_info=True)

        # Break out 403 errors for multiple tries
        if resp.status in [403, 429]:
            redis.hincrby("403errors", url, 1)
            await redis.srem('domainbeingcrawled:active', current_netloc)
            number_of_errors = await redis.hget('403errors', url)
            number_of_errors = int(number_of_errors.decode('utf8'))
            if number_of_errors >= 5:
                await Page.create(
                    page=url,
                    errors=[],
                    page_response=resp.status,
                    domain=domain.id
                )
                await redis.srem('pagestobecrawled:queue', url)

            return
        soup = BeautifulSoup(await resp.text(), "html.parser")
        visible_words = get_text(soup)
        wrong_words = await check_if_spelled_right(redis, words=visible_words)

        try:
            await Page.create(
                page=url,
                errors=wrong_words,
                page_response=resp.status,
                domain=domain.id
            )
            await extract_and_queue_local_links(soup=soup, root_domain=resp.host, redis=redis)
        except Exception as e:
            logging.error(e)
        print(f'successfully processed {url}')
        print(f'About to pop {current_netloc}')
        await redis.srem('pagestobecrawled:queue', url)
        await redis.srem('domainbeingcrawled:active', current_netloc)
        print('popped!')


# Controller function contains the tcp_session
async def get_multiple_pages(loop):
    # Auto close the loop at the end
    # with closing(asyncio.get_event_loop()) as loop:
    # timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(keepalive_timeout=10, limit=50,
                                                                               verify_ssl=False)) as open_session:
        # handle aiohttp.client_exceptions.ServerDisconnectedError
        # initiate the redis instance
        redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
        # Push the initial pages
        # This loop primarily works because the page is only removed from the queue AFTER it has been scraped
        while await redis.scard('pagestobecrawled:queue') > 0:
            open_spots_for_domains = 200 - await redis.scard('domainbeingcrawled:active')

            if open_spots_for_domains <= 200:
                # TODO: NO
                if await redis.scard('pagestobecrawled:queue') == 0:
                    break
                # loop through this up to 200 times
                new_tasks = []
                new_urls = []
                # Get a set of random pages
                rand_pages = await redis.srandmember('pagestobecrawled:queue', open_spots_for_domains)
                # We've got 200 url's
                for rand_page in rand_pages:
                    rand_page_netloc = urlparse(rand_page).netloc
                    # If the page exists in the active queue, don't add it
                    if await redis.sismember("domainbeingcrawled:active", rand_page_netloc):
                        continue
                    # The domain is ready to be crawled
                    # Add it to the domainbeingcrawled:active set
                    await redis.sadd('domainbeingcrawled:active', rand_page_netloc)
                    # add it to the loop
                    task = asyncio.create_task(parse_page(redis, rand_page.decode("utf-8"), open_session))
                    new_tasks.append(task)
                    new_urls.append(rand_page)
                    # If we're just topping off from 190 to 200 tasks, we should break this loop
                    if len(new_tasks) == open_spots_for_domains:
                        print('Breaking the loop TODO: test this')
                        continue
                print(f'about to add {new_urls} to the queue')
                await asyncio.gather(*new_tasks)
            print('sleeping for 1.5!')
            await asyncio.sleep(1.5)

        redis.close()
        await redis.wait_closed()
