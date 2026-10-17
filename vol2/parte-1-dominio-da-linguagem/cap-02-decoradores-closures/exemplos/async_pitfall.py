"""Decorador síncrono em função assíncrona: o timer que mente."""
import asyncio
import functools
import inspect
import time


def timer_wrong(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)   # só CRIA a corrotina
        print(f"wrong: {(time.perf_counter() - start) * 1e3:.2f} ms")
        return result
    return wrapper


def timer_right(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            print(f"right: {(time.perf_counter() - start) * 1e3:.0f} ms")
    return wrapper


@timer_wrong
async def job_a():
    await asyncio.sleep(0.05)
    return "a"


@timer_right
async def job_b():
    await asyncio.sleep(0.05)
    return "b"


async def main():
    print(await job_a())
    print(await job_b())


asyncio.run(main())
print(inspect.iscoroutinefunction(job_a.__wrapped__))
print(inspect.iscoroutinefunction(job_a))
print(inspect.iscoroutinefunction(job_b))
