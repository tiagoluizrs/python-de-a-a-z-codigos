"""Gabarito do exercício 6."""
import asyncio

_DONE = object()


async def merge_streams(*streams):
    if not streams:
        return
    queue = asyncio.Queue()

    async def pump(stream):
        try:
            async for item in stream:
                await queue.put(("item", item))
        except BaseException as error:
            if isinstance(error, asyncio.CancelledError):
                raise
            await queue.put(("error", error))
            return
        await queue.put(("done", _DONE))

    tasks = [asyncio.create_task(pump(stream)) for stream in streams]
    remaining = len(tasks)
    try:
        while remaining:
            kind, payload = await queue.get()
            if kind == "item":
                yield payload
            elif kind == "error":
                raise payload
            else:
                remaining -= 1
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
