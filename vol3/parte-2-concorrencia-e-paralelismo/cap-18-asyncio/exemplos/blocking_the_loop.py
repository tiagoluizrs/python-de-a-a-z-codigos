"""O pecado capital: bloquear o laço de eventos."""
import asyncio
import time


async def ticker(stamps, n=12):
    for _ in range(n):
        stamps.append(time.perf_counter())
        await asyncio.sleep(0.01)


async def max_gap_ms(blocker):
    stamps = []
    task = asyncio.create_task(ticker(stamps))
    await asyncio.sleep(0.03)
    await blocker()
    await task
    return max(b - a for a, b in zip(stamps, stamps[1:])) * 1e3


async def block_with_sleep():
    time.sleep(0.3)                                  # BLOQUEIA o laço inteiro


async def block_with_thread():
    await asyncio.to_thread(time.sleep, 0.3)         # o laço segue livre


async def block_with_async_sleep():
    await asyncio.sleep(0.3)


async def main():
    print("um 'relógio' deveria bater a cada 10 ms. Maior intervalo entre batidas:")
    print(f"  com time.sleep(0,3) na corrotina : {await max_gap_ms(block_with_sleep):6.1f} ms")
    print(f"  com asyncio.to_thread(sleep)     : {await max_gap_ms(block_with_thread):6.1f} ms")
    print(f"  com await asyncio.sleep(0,3)     : {await max_gap_ms(block_with_async_sleep):6.1f} ms")


asyncio.run(main(), debug=False)

# Modo debug: o próprio asyncio avisa sobre callbacks lentos (slow_callback_duration, 0,1 s por padrão)
import logging

logging.basicConfig(level=logging.WARNING, format="  [log] %(message)s")


async def slow_one():
    time.sleep(0.2)


print("com debug=True:")
asyncio.run(slow_one(), debug=True)
