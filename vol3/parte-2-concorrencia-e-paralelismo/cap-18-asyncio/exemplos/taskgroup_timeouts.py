"""Concorrência estruturada: TaskGroup, ExceptionGroup, timeout, cancelamento."""
import asyncio


async def work(name, delay):
    await asyncio.sleep(delay)
    return name


async def boom(n):
    await asyncio.sleep(0.01 * n)
    raise ValueError(f"falha {n}")


async def main():
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(work(f"t{i}", 0.02 * i)) for i in range(3)]
    print("TaskGroup esperou todas:", [t.result() for t in tasks])

    # uma falha cancela as irmãs e sai como ExceptionGroup
    other = None
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(boom(1))
            tg.create_task(boom(2))
            other = tg.create_task(work("longa", 5))
    except* ValueError as group:
        print("except* recebeu:", [str(e) for e in group.exceptions], "| a longa foi cancelada:", other.cancelled())

    # timeout: o jeito moderno (3.11+)
    try:
        async with asyncio.timeout(0.05):
            await asyncio.sleep(5)
    except TimeoutError:
        print("asyncio.timeout(0,05) -> TimeoutError")
    try:
        await asyncio.wait_for(asyncio.sleep(5), timeout=0.05)
    except TimeoutError:
        print("asyncio.wait_for       -> TimeoutError")

    # cancelamento: CancelledError é injetado no await; faça a limpeza e RE-LEVANTE
    async def with_cleanup():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            print("  limpeza feita antes de morrer")
            raise

    task = asyncio.create_task(with_cleanup())
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("task.cancelled() =", task.cancelled())

    # shield: protege uma tarefa de ser cancelada junto com quem espera
    inner = asyncio.create_task(work("protegida", 0.1))
    try:
        async with asyncio.timeout(0.02):
            await asyncio.shield(inner)
    except TimeoutError:
        pass
    print("a espera estourou, mas a tarefa protegida segue:", await inner)

    # NOVO no 3.15: TaskGroup.cancel()
    async with asyncio.TaskGroup() as tg:
        a = tg.create_task(work("a", 5))
        b = tg.create_task(work("b", 5))
        await asyncio.sleep(0.01)
        tg.cancel()
    print("TaskGroup.cancel() (3.15) cancelou o grupo:", a.cancelled(), b.cancelled())


asyncio.run(main())
