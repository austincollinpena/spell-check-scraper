from gino import Gino
from scraper import config

print(config.DB_DSN)

import asyncio

gino_db = Gino()

async def main():
    await gino_db.set_bind(config.DB_DSN)

asyncio.get_event_loop().run_until_complete(main())

# Import your models here so Alembic will pick them up
from db.models import *
