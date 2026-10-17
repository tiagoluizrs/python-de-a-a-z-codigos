"""async for, async with e geradores assíncronos."""
import asyncio
import contextlib


async def ticks(n, delay=0.01):
    for i in range(n):
        await asyncio.sleep(delay)
        yield i


@contextlib.asynccontextmanager
async def connection(name):
    print(f"  abre {name}")
    try:
        yield f"<{name}>"
    finally:
        print(f"  fecha {name}")


class Paginator:
    """Iterador assíncrono escrito à mão: __aiter__ e __anext__."""

    def __init__(self, pages):
        self._pages = iter(pages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            page = next(self._pages)
        except StopIteration:
            raise StopAsyncIteration from None
        await asyncio.sleep(0.01)
        return page


async def main():
    print("async for:", [i async for i in ticks(5)])
    print("compreensão assíncrona com filtro:", [i async for i in ticks(10) if i % 3 == 0])
    async with connection("db") as conn:
        print("  usando", conn)
    print("iterador à mão:", [p async for p in Paginator(["p1", "p2", "p3"])])

    # um gerador assíncrono interrompido precisa de aclose() (aclosing garante)
    async with contextlib.aclosing(ticks(100)) as gen:
        async for i in gen:
            if i == 2:
                break
    print("gerador fechado de forma limpa depois do break")

    # as_completed: um iterador na ordem de TÉRMINO
    async def job(n, d):
        await asyncio.sleep(d)
        return n

    order = [await c for c in asyncio.as_completed([job(3, 0.03), job(1, 0.01), job(2, 0.02)])]
    print("as_completed:", order)


asyncio.run(main())
