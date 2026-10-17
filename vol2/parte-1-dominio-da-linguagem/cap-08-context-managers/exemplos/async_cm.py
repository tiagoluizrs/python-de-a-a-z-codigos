"""async with: __aenter__ e __aexit__ (detalhes no Capítulo 18 do Volume 3)."""
import asyncio
from contextlib import asynccontextmanager


class AsyncResource:
    async def __aenter__(self):
        await asyncio.sleep(0)               # pode esperar (abrir conexão...)
        print("  aenter")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(0)
        print("  aexit")
        return False


@asynccontextmanager
async def timer_like(name):
    print(f"  inicio {name}")
    try:
        yield name
    finally:
        print(f"  fim {name}")


async def main():
    async with AsyncResource() as r:
        print("  corpo", type(r).__name__)
    async with timer_like("job") as name:
        print("  corpo", name)


asyncio.run(main())
