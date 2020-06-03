from scraper import config
from db import gino_db
import asyncio
import csv
from more_itertools import chunked
from db.models import Domain



async def bulk_insert_final_list():
    await gino_db.set_bind(config.DB_DSN, echo=True)
    with open('../clean_data/just_values.csv', encoding='utf8') as clean_domains_csv:
        clean_domains = csv.DictReader(clean_domains_csv)
        # Read the values into a nice formal
        all_domains = []
        for value in clean_domains:

            all_domains.append(f'http://{value["0"]}')

        chunked_domains = list(chunked(all_domains, 1000))
        # Seperate out 1,000 values
        for chunk in chunked_domains:
            # Get the individual domain
            values_to_insert = []
            for individual_domain in chunk:
                values_to_insert.append({"domain":individual_domain})
            await Domain.insert().gino.all(values_to_insert)



asyncio.get_event_loop().run_until_complete(bulk_insert_final_list())
