"""Gabarito do exercício 1."""
import asyncio


async def gather_limited(factories, limit):
    if limit < 1:
        raise ValueError("limit >= 1")
    factories = list(factories)
    if not factories:
        return []
    semaphore = asyncio.Semaphore(limit)

    async def run(factory):
        async with semaphore:
            return await factory()

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(run(factory)) for factory in factories]
    return [task.result() for task in tasks]
