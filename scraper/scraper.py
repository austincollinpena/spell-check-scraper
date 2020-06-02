import aiohttp
import aioredis
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Module Imports
from scraper.utils.scraping.get_text import get_text
from scraper.utils.scraping.extract_local_links import extract_and_queue_local_links
from scraper.utils.scraping.check_if_spelled_right import check_if_spelled_right
from db.models.models import Domain, Page


async def parse_page(redis, url: str, session) -> None:  # TODO: Proxy!
    async with session.get(url, ssl=False, allow_redirects=True, proxy="http://173.234.250.41:3128") as resp:
        soup = BeautifulSoup(await resp.text(), "html.parser")
        visible_words = get_text(soup)
        wrong_words = await check_if_spelled_right(redis, words=visible_words)
        current_netloc = urlparse(url).netloc
        try:
            domain = await Domain.query.where(Domain.domain == f'http://{current_netloc}').gino().first()
            await Page.create(
                page=url,
                errors=wrong_words,
                page_response=resp.status,
                domain=domain.id
            )
        except Exception as e:
            print(e)
        # Add the local links found on the page
        await extract_and_queue_local_links(soup=soup, root_domain=resp.host, redis=redis)


# Controller function contains the tcp_session
async def get_multiple_pages(loop):
    # Auto close the loop at the end
    # with closing(asyncio.get_event_loop()) as loop:
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(loop=loop, timeout=timeout) as open_session:
        # handle aiohttp.client_exceptions.ServerDisconnectedError
        # initiate the redis instance
        redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")

        # TODO: Add all of the pagestobecrawled to the sites:{root_domain}:pages so they don't get re-added
        # TODO: change pagestobecrawled:queue to a set everywhere
        # TODO: Add spelling errors to the db
        # TODO: Start with tests
        while await redis.scard('pagestobecrawled:queue') > 0:
            open_spots_for_domains = 200 - redis.scard('domainbeingcrawled:active')
            while open_spots_for_domains < 200:
                if await redis.scard('pagestobecrawled:queue') == 0:
                    break
                # Get the next value
                rand_page = await redis.srandmember('pagestobecrawled:queue')
                # get the netloc of the page
                rand_page_netloc = urlparse(rand_page).netloc
                # If the page exists in the active queue, don't add it
                if await redis.sismember("domainbeingcrawled:active", rand_page_netloc):
                    break
                # The domain is ready to be crawled
                # Remove it from the pagestobecrawled:queue
                await redis.srem('pagestobecrawled:queue', rand_page)
                # Add it to the domainbeingcrawled:active set
                await redis.sadd('domainbeingcrawled:active', rand_page)
                # add it to the loop
                loop.create_task(parse_page(redis, rand_page.decode("utf-8"), open_session))
            # Don't just keep running this loop for no reason, 5 seconds should be plenty to re add new tasks
            await asyncio.sleep(5)
        redis.close()
        await redis.wait_closed()
