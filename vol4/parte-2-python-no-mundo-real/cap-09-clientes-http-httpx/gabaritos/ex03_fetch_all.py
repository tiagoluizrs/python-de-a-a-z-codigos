"""Gabarito do exercício 3."""
import asyncio

import httpx


async def fetch_all(client, urls, *, concurrency=10):
    if concurrency < 1:
        raise ValueError("concurrency >= 1")
    urls = list(urls)
    if not urls:
        return []
    semaphore = asyncio.Semaphore(concurrency)

    async def one(url):
        async with semaphore:
            try:
                return await client.get(url)
            except httpx.RequestError as error:
                return error

    return await asyncio.gather(*(one(url) for url in urls))
