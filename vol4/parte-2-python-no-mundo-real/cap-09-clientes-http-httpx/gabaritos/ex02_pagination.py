"""Gabarito do exercício 2."""


def paginate(client, url, params=None, *, items_key="items", next_key="next", page_param="page", start=1, max_pages=None):
    page, fetched = start, 0
    while page is not None and (max_pages is None or fetched < max_pages):
        response = client.get(url, params={**(params or {}), page_param: page})
        response.raise_for_status()
        data = response.json()
        fetched += 1
        yield from data[items_key]
        page = data.get(next_key)


async def apaginate(client, url, params=None, *, items_key="items", next_key="next", page_param="page", start=1, max_pages=None):
    page, fetched = start, 0
    while page is not None and (max_pages is None or fetched < max_pages):
        response = await client.get(url, params={**(params or {}), page_param: page})
        response.raise_for_status()
        data = response.json()
        fetched += 1
        for item in data[items_key]:
            yield item
        page = data.get(next_key)
