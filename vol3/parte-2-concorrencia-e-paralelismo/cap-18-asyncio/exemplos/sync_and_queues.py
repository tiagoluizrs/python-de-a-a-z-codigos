"""Semaphore, Lock, Event e Queue em asyncio (as versões assíncronas do Capítulo 15)."""
import asyncio


async def limited(sem, state):
    async with sem:
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.01)
        state["now"] -= 1


async def producer(queue, n):
    for i in range(n):
        await queue.put(i)                       # espera se a fila está cheia (contrapressão)
    await queue.put(None)


async def consumer(queue, out):
    while (item := await queue.get()) is not None:
        out.append(item * item)
        queue.task_done()
    queue.task_done()


async def main():
    sem, state = asyncio.Semaphore(5), {"now": 0, "peak": 0}
    await asyncio.gather(*(limited(sem, state) for _ in range(50)))
    print("50 tarefas, Semaphore(5): pico de simultâneas =", state["peak"])

    queue, out = asyncio.Queue(maxsize=3), []
    await asyncio.gather(producer(queue, 20), consumer(queue, out))
    print("produtor/consumidor com Queue(maxsize=3):", out[:6], "...", len(out), "itens")

    # Lock: protege seções com await no meio (sem Lock, outras tarefas entram no intervalo)
    counter, lock = 0, asyncio.Lock()

    async def safe_increment():
        nonlocal counter
        async with lock:
            current = counter
            await asyncio.sleep(0)               # cede o laço entre ler e escrever
            counter = current + 1

    await asyncio.gather(*(safe_increment() for _ in range(100)))
    print("100 incrementos com Lock e await no meio:", counter)

    counter = 0

    async def unsafe_increment():
        nonlocal counter
        current = counter
        await asyncio.sleep(0)
        counter = current + 1

    await asyncio.gather(*(unsafe_increment() for _ in range(100)))
    print("100 incrementos SEM Lock e com await no meio:", counter, "(corrida: o await é um ponto de troca)")

    event = asyncio.Event()
    seen = []

    async def waiter(i):
        await event.wait()
        seen.append(i)

    waiters = [asyncio.create_task(waiter(i)) for i in range(3)]
    await asyncio.sleep(0.01)
    before = list(seen)
    event.set()
    await asyncio.gather(*waiters)
    print("Event: antes do set", before, "| depois", sorted(seen))

    # Queue.shutdown (3.13+)
    q = asyncio.Queue()
    await q.put("resto")
    q.shutdown()
    print("Queue.shutdown(): get ->", await q.get(), end=" | ")
    try:
        await q.get()
    except asyncio.QueueShutDown:
        print("QueueShutDown")


asyncio.run(main())
