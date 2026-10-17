"""Corrotinas, await, tarefas e o ganho de gather."""
import asyncio
import time
import warnings


async def fetch(n, delay):
    await asyncio.sleep(delay)                    # cede o controle ao laço enquanto espera
    return n * 10


async def main():
    coro = fetch(1, 0.1)
    print("chamar uma async def NÃO executa:", type(coro).__name__)
    print("await executa e devolve:", await coro)

    start = time.perf_counter()
    for i in range(5):
        await fetch(i, 0.1)
    print(f"5 esperas de 0,1 s UMA após a outra : {time.perf_counter() - start:.2f} s")

    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(i, 0.1) for i in range(5)))
    print(f"5 esperas de 0,1 s com gather        : {time.perf_counter() - start:.2f} s -> {results}")

    start = time.perf_counter()
    await asyncio.gather(*(fetch(i, 0.1) for i in range(1000)))
    print(f"1.000 esperas de 0,1 s com gather    : {time.perf_counter() - start:.2f} s (em UMA thread)")

    task = asyncio.create_task(fetch(7, 0.05))    # agenda JÁ, sem esperar
    print("create_task agenda; o resultado vem do await:", await task, "| done =", task.done())

    # esquecer o await: a corrotina nunca roda
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fetch(9, 0.0)
        import gc
        gc.collect()
    print("sem await:", [str(w.message) for w in caught][:1])


asyncio.run(main())
