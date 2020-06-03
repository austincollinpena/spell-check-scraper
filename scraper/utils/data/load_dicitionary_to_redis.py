import aioredis
from .load_txt_to_python_set import load_words
from more_itertools import chunked
from os import getcwd, path


async def load_data(override=False):
    redis = await aioredis.create_redis_pool('redis://localhost', password="sOmE_sEcUrE_pAsS")
    values = await redis.scard('dict:all')

    if values < 1000000 or override:
        all_english_words = load_words(
            path.join(getcwd(), "./scraper/utils/data/english_dictionary/wlist_match2.txt")).union(
            load_words(path.join(getcwd(), "./scraper/utils/data/english_dictionary/wlist_match1.txt")).union(
                load_words(path.join(getcwd(), "./scraper/utils/data/english_dictionary/personal_whitelist.txt"))))

        chunks = list(chunked(all_english_words, 10000))
        for chunk in chunks:
            await redis.sadd('dict:all', *chunk)
        new_len = await redis.scard('dict:all')
        print(f'Database seeded with {new_len} values')
    else:
        print(f'data already loaded with {values} values')
        return
