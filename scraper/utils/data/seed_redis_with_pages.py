import aioredis
from urllib.parse import urlparse


async def load_redis_data(list_of_domains: list):
    print('pushing the data')
    redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
    # Add
    await redis.sadd('pagestobecrawled:queue', *list_of_domains)

    for page in list_of_domains:
        parsed_url = urlparse(page)
        # Avoid re-crawling domain.com and domain.com/
        correct_path = '/' if parsed_url.path == '' else parsed_url.path
        await redis.sadd(f'sites:{parsed_url.netloc}:pages', correct_path)
