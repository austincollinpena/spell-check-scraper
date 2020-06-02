import aioredis


async def load_redis_data(list_of_domains: list):
    print('pushing the data')
    redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
    # TODO: Need to add them to the correct queue here
    redis.lpush(f'pagestobecrawled:queue', *list_of_domains)
