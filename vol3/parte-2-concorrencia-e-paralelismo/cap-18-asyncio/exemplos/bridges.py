"""Pontes: código bloqueante, threads chamando o laço, contexto."""
import asyncio
import contextvars
import threading
import time

request_id = contextvars.ContextVar("request_id", default="-")


def blocking_io(seconds):
    time.sleep(seconds)
    return threading.current_thread().name


def read_request_id():
    return request_id.get()


async def main():
    loop = asyncio.get_running_loop()

    start = time.perf_counter()
    names = await asyncio.gather(*(asyncio.to_thread(blocking_io, 0.2) for _ in range(5)))
    print(f"5 bloqueantes via to_thread: {time.perf_counter() - start:.2f} s | threads: {sorted(set(names))[:2]}...")

    # contextvars: tarefas COPIAM o contexto; to_thread também
    request_id.set("req-42")

    async def in_task():
        return request_id.get()

    print("contexto numa tarefa:", await asyncio.create_task(in_task()), "| em to_thread:", await asyncio.to_thread(read_request_id))

    async def child_sets():
        request_id.set("filha")

    await asyncio.create_task(child_sets())
    print("a tarefa filha mudou o contexto dela, não o do pai:", request_id.get())

    # de outra thread para o laço: run_coroutine_threadsafe e call_soon_threadsafe
    async def answer(x):
        await asyncio.sleep(0.01)
        return x * 2

    holder = {}

    def from_thread():
        holder["value"] = asyncio.run_coroutine_threadsafe(answer(21), loop).result(timeout=2)

    thread = threading.Thread(target=from_thread)
    thread.start()
    await asyncio.to_thread(thread.join)           # espera SEM bloquear o laço
    print("run_coroutine_threadsafe, de outra thread:", holder["value"])

    done = asyncio.Event()
    threading.Thread(target=lambda: loop.call_soon_threadsafe(done.set)).start()
    await asyncio.wait_for(done.wait(), 2)
    print("call_soon_threadsafe acordou o laço a partir de outra thread")


asyncio.run(main())
