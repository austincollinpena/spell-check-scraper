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


async def parse_page(redis, url: str, session) -> None:
    header = Headers()

    async with session.get(url, headers=header.generate(), ssl=False, allow_redirects=True,
                           proxy=random_proxy()) as resp:
        soup = BeautifulSoup(await resp.text(), "html.parser")
        visible_words = get_text(soup)
        wrong_words = await check_if_spelled_right(redis, words=visible_words)
        current_netloc = urlparse(url).netloc
        # try:


        domain = await Domain.query.where(Domain.domain == f'http://{current_netloc}').gino().first()

        await Page.create(
            page=url,
            errors=wrong_words,
            page_response=resp.status,
            domain=domain.id
        )
        # except Exception as e:
        #     print(e)
        # Add the local links found on the page
        await extract_and_queue_local_links(soup=soup, root_domain=resp.host, redis=redis)
        # TODO: Pop from queue AND :active queue here
        print(f'successfully processed {url}')
        print(f'About to pop {current_netloc}')
        await redis.srem('pagestobecrawled:queue', url)
        await redis.srem('domainbeingcrawled:active', current_netloc)


# Controller function contains the tcp_session
async def get_multiple_pages(loop):
    # Auto close the loop at the end
    # with closing(asyncio.get_event_loop()) as loop:
    # timeout = aiohttp.ClientTimeout(total=60)
    async with gino_db.with_bind(config.DB_DSN, echo=True) as engine:
        async with aiohttp.ClientSession(loop=loop) as open_session:
            # handle aiohttp.client_exceptions.ServerDisconnectedError
            # initiate the redis instance
            redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
            # Push the initial pages
            pages = await redis.smembers('pagestobecrawled:queue')
            initial_tasks = []
            for page in pages:
                task = asyncio.create_task(parse_page(redis, page.decode("utf-8"), open_session))
                initial_tasks.append(task)
            await asyncio.gather(*initial_tasks)

            # This loop primarily works because the page is only removed from the queue AFTER it has been scraped
            while await redis.scard('pagestobecrawled:queue') > 0:
                open_spots_for_domains = 200 - await redis.scard('domainbeingcrawled:active')
                # TODO: This loop seems to get stuck
                if open_spots_for_domains < 200:
                    # TODO: Add the number of tasks to get to 200
                    print('fewer open spots')
                    if await redis.scard('pagestobecrawled:queue') == 0:
                        break
                    # Get the next value
                    rand_page = await redis.srandmember('pagestobecrawled:queue')
                    # get the netloc of the page
                    rand_page_netloc = urlparse(rand_page).netloc
                    # If the page exists in the active queue, don't add it
                    if await redis.sismember("domainbeingcrawled:active", rand_page_netloc):
                        await asyncio.sleep(5)
                        continue
                    # The domain is ready to be crawled
                    # Add it to the domainbeingcrawled:active set
                    await redis.sadd('domainbeingcrawled:active', rand_page)
                    # add it to the loop
                    # loop.create_task(parse_page(redis, rand_page.decode("utf-8"), open_session))
                    task = asyncio.create_task(parse_page(redis, rand_page.decode("utf-8"), open_session))
                    await asyncio.gather(task)

                # Don't just keep running this loop for no reason, 5 seconds should be plenty to re add new tasks
                await asyncio.sleep(5)

            redis.close()
            await redis.wait_closed()
