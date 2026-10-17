"""Filas DENTRO do processo (threads e asyncio): ótimas para suavizar picos, inúteis para não perder trabalho."""
import asyncio
import queue
import subprocess
import sys
import textwrap
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# 1. queue.Queue + threads de trabalho: o padrão produtor/consumidor
jobs: queue.Queue = queue.Queue()
done: list[int] = []


def worker():
    while True:
        item = jobs.get()
        if item is None:
            jobs.task_done()
            return
        time.sleep(0.01)                           # 10 ms de E/S
        done.append(item)
        jobs.task_done()


def drain(n_workers: int, n_jobs: int = 200) -> float:
    done.clear()
    threads = [threading.Thread(target=worker) for _ in range(n_workers)]
    for t in threads:
        t.start()
    start = time.perf_counter()
    for i in range(n_jobs):
        jobs.put(i)
    for _ in threads:
        jobs.put(None)
    jobs.join()
    elapsed = time.perf_counter() - start
    for t in threads:
        t.join()
    return elapsed


print("200 tarefas de 10 ms com queue.Queue:")
for n in (1, 4, 16):
    print(f"  {n:>2} threads: {drain(n) * 1e3:7.0f} ms (ideal {200 * 10 / n:6.0f} ms)")

# 2. a fila com TETO (maxsize) aplica contrapressão: o produtor ESPERA em vez de encher a memória
bounded: queue.Queue = queue.Queue(maxsize=5)
stalls = []


def slow_consumer():
    for _ in range(30):
        time.sleep(0.005)
        bounded.get()


consumer = threading.Thread(target=slow_consumer)
consumer.start()
start = time.perf_counter()
for i in range(30):
    t0 = time.perf_counter()
    bounded.put(i)
    stalls.append(time.perf_counter() - t0)
consumer.join()
print(f"\nfila com maxsize=5: o produtor esperou {sum(s > 0.001 for s in stalls)} vezes; total {(time.perf_counter() - start) * 1e3:.0f} ms (o ritmo do consumidor manda)")
unbounded = queue.Queue()
for i in range(200_000):
    unbounded.put(i)
print(f"fila SEM teto: aceitou 200.000 itens sem reclamar (qsize={unbounded.qsize():,}): em um pico, a memória é o limite")


# 3. asyncio.Queue: o mesmo, sem threads
async def async_drain(n_workers: int, n_jobs: int = 200) -> float:
    q: asyncio.Queue = asyncio.Queue()
    results = []

    async def consume():
        while True:
            item = await q.get()
            await asyncio.sleep(0.01)
            results.append(item)
            q.task_done()

    tasks = [asyncio.create_task(consume()) for _ in range(n_workers)]
    start = time.perf_counter()
    for i in range(n_jobs):
        q.put_nowait(i)
    await q.join()
    elapsed = time.perf_counter() - start
    for t in tasks:
        t.cancel()
    return elapsed


print("\n200 tarefas de 10 ms com asyncio.Queue:")
for n in (1, 4, 16, 200):
    print(f"  {n:>3} consumidores: {asyncio.run(async_drain(n)) * 1e3:7.0f} ms (ideal {200 * 10 / n:6.0f} ms)")

# 4. o erro silencioso do ThreadPoolExecutor: a exceção fica guardada no Future, e ninguém olha
def boom(i):
    if i % 2:
        raise RuntimeError(f"falhou {i}")
    return i


with ThreadPoolExecutor(2) as pool:
    futures = [pool.submit(boom, i) for i in range(6)]
print(f"\nsubmit() sem olhar o resultado: 0 erros visíveis, mas {sum(f.exception() is not None for f in futures)} de 6 tarefas FALHARAM (use future.result() ou add_done_callback)")

# 5. o limite fundamental: tudo isso mora na memória do processo
code = textwrap.dedent("""
    import os, queue, threading, time
    q = queue.Queue()
    done = []
    def run():
        while True:
            q.get(); time.sleep(0.2); done.append(1); q.task_done()
    threading.Thread(target=run, daemon=True).start()
    for i in range(10):
        q.put(i)
    time.sleep(0.5)
    print("processadas antes da queda:", len(done), "| na fila:", q.qsize(), flush=True)
    os._exit(1)                                            # o processo morre (um kill, um deploy, um OOM)
""")
out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
print(f"\nqueda do processo com 10 tarefas na fila em memória: {out.stdout.strip()} -> as que restavam (7 ou mais) SUMIRAM, sem rastro")
