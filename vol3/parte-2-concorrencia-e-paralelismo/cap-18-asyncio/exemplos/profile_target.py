"""Alvo para o profiling.sampling: uma tarefa de CPU e duas esperas, de 0,5 s cada."""
import asyncio
import time


async def cpu():
    start = time.perf_counter()
    while time.perf_counter() - start < 0.5:
        sum(range(1000))


async def io():
    await asyncio.sleep(0.5)


async def main():
    await asyncio.gather(cpu(), io(), io())


asyncio.run(main())
