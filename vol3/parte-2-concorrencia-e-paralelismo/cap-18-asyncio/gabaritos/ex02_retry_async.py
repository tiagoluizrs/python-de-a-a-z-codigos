"""Gabarito do exercício 2."""
import asyncio


async def retry_async(factory, *, retries=3, delay=0.0, attempt_timeout=None, retry_on=(Exception,), sleep=asyncio.sleep):
    if retries < 0:
        raise ValueError("retries >= 0")
    failures = 0
    while True:
        try:
            if attempt_timeout is None:
                return await factory()
            async with asyncio.timeout(attempt_timeout):
                return await factory()
        except retry_on:
            if failures >= retries:
                raise
            if delay:
                await sleep(delay * 2**failures)
            failures += 1
