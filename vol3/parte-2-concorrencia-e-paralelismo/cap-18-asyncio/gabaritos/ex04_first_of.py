"""Gabarito do exercício 4."""
import asyncio


async def first_of(*factories):
    if not factories:
        raise ValueError("nenhuma corrotina")
    tasks = [asyncio.create_task(factory()) for factory in factories]
    errors = []
    pending = set(tasks)
    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if task.exception() is None:
                    return task.result()
                errors.append(task.exception())
        raise ExceptionGroup("todas falharam", errors)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
