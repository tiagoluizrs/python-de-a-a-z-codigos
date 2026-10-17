"""Gabarito do exercício 3."""
import asyncio


async def run_pipeline(items, worker, workers=3, queue_size=5):
    if workers < 1 or queue_size < 1:
        raise ValueError("workers e queue_size >= 1")
    results = {}
    queue = asyncio.Queue(maxsize=queue_size)
    total = 0

    async def produce():
        nonlocal total
        for index, item in enumerate(items):
            await queue.put((index, item))
            total = index + 1
        for _ in range(workers):
            await queue.put(None)

    async def consume():
        while (job := await queue.get()) is not None:
            index, item = job
            results[index] = await worker(item)

    async with asyncio.TaskGroup() as group:
        group.create_task(produce())
        for _ in range(workers):
            group.create_task(consume())
    return [results[i] for i in range(total)]
