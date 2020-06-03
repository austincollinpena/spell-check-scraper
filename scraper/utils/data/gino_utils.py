from db import db
from db.models import Domain
from scraper import config


async def init_db():
    return await db.with_bind(config.DB_DSN, echo=True)


async def get_list_of_domains():
    domains = await Domain.query.gino.all()
    return [domain.domain for domain in domains]
