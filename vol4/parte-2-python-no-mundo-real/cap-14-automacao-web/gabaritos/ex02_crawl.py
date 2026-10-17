"""Gabarito do exercício 2."""
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def crawl(fetch, start_url, max_pages=50):
    urls, items, seen = [], [], set()
    url = start_url
    while url is not None and url not in seen and len(urls) < max_pages:
        html = fetch(url)
        if html is None:
            break
        seen.add(url)
        urls.append(url)
        soup = BeautifulSoup(html, "lxml")
        items += [node.get_text(strip=True) for node in soup.select(".name")]
        link = soup.select_one("a[rel=next]")
        url = urljoin(url, link["href"]) if link and link.get("href") else None
    return urls, items
