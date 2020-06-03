import aioredis
from urllib.parse import urlparse


async def load_redis_data(list_of_domains: list):
    print('pushing the data')
    redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
    # Add
    redis.sadd('pagestobecrawled:queue', *list_of_domains)

    for page in list_of_domains:
        netloc = urlparse(page).netloc
        redis.sadd('domainbeingcrawled:active', netloc)
        redis.sadd(f'sites:{netloc}:pages', page)
