from urllib.parse import urlparse, urljoin
import re
from aiologger import Logger
import logging


async def extract_and_queue_local_links(soup, root_domain: str, redis):
    href_tags = soup.find_all("a", href=True)
    links = [a['href'] for a in href_tags]
    prog = re.compile('http.*(wp-content|.png|.jpg|.jpeg|.svg)')
    valid_links = []
    # parse away query params
    for url in links:
        try:
            valid_links.append(urljoin(url, urlparse(url).path))
        except Exception as e:
            logging.warning(f'Failed at extracting {url}', exc_info=True)

    for link in valid_links:
        # STOP anything from wp-content, .png, .jpg, or others
        if urlparse(link).netloc == root_domain \
                and not await redis.sismember(f'sites:{root_domain}:pages', link) \
                and not prog.match(link):
            await redis.sadd(f'sites:{root_domain}:pages', link)
            # Add the domain to the queue
            await redis.sadd('pagestobecrawled:queue', link)
