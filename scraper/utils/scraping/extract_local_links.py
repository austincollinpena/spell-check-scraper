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
    # TODO: why isn't this working to stop things?
    for link in valid_links:
        # STOP anything from wp-content, .png, .jpg, or others
        parsed_url = urlparse(link)
        correct_path = '/' if parsed_url.path == '' else parsed_url.path
        # handle relative links
        if link.startswith("/"):
            link = f'http://{root_domain}{link}'
        if urlparse(link).netloc == root_domain \
                and not await redis.sismember(f'sites:{root_domain}:pages', correct_path) \
                and not prog.match(link):
            # Only add the path to the set on the domain to avoid any http/www/https mixups!
            await redis.sadd(f'sites:{root_domain}:pages', correct_path)
            # Add the domain to the queue
            await redis.sadd('pagestobecrawled:queue', link)
        # If there are more than 1000 links to a site, stop scraping
        active_links = await redis.scard(f'sites:{root_domain}:pages')
        active_links = int(active_links)
        if active_links >= 1000:
            await redis.sdiffstore('pagestobecrawled:queue', 'pagestobecrawled:queue', f'sites:{root_domain}:pages')
