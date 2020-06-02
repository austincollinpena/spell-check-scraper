from . import config
from db import db
import asyncio
from .utils.data.load_dicitionary_to_redis import load_data
from .utils.data.seed_redis_with_pages import load_redis_data

if __name__ == "__main__":
    await db.set_bind(config.DB_DSN, echo=True)
    # Load the dicitionary. Pass through override=True to force reload after the first run
    asyncio.run(load_data())
    # TODO: Get the domains and mark them as gotten
    # Add the domains to Redis
    asyncio.run(load_redis_data(list_of_domains=[]))
