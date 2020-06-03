from db import gino_db
from db.models import Domain
from scraper import config


async def init_db():
    engine = await gino_db.set_bind(config.DB_DSN)
    domain = await Domain.query.where(Domain.domain == 'http://equipomedia.com').gino.first()
    domain


async def get_list_of_domains():
    domains = await Domain.query.gino.all()
    return [domain.domain for domain in domains]
