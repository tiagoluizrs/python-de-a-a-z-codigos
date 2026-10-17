"""Gabarito do exercício 5."""
import asyncio


async def collect_with_timeout(factories, timeout):
    factories = list(factories)
    if not factories:
        return {}, []
    if timeout <= 0:
        return {}, list(range(len(factories)))
    tasks = [asyncio.create_task(factory()) for factory in factories]
    try:
        done, pending = await asyncio.wait(tasks, timeout=timeout)
        for task in done:
            if task.exception() is not None:
                raise task.exception()
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    results = {i: task.result() for i, task in enumerate(tasks) if task in done}
    late = sorted(i for i, task in enumerate(tasks) if task in pending)
    return results, late
