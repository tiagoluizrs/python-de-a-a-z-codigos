"""Custos das threads: criar, quantas cabem, e o preço de uma trava disputada."""
import threading
import time


def measure_start(n):
    start = time.perf_counter()
    threads = [threading.Thread(target=lambda: None) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return (time.perf_counter() - start) / n


for n in (100, 1_000):
    print(f"criar+iniciar+esperar {n:>5} threads vazias: {measure_start(n) * 1e6:7.0f} us cada")

# Muitas threads vivas ao mesmo tempo (todas esperando)
stop = threading.Event()
start = time.perf_counter()
alive = [threading.Thread(target=stop.wait) for _ in range(2_000)]
for t in alive:
    t.start()
print(f"2.000 threads vivas e esperando: criadas em {time.perf_counter() - start:.2f} s | active_count = {threading.active_count()}")
stop.set()
for t in alive:
    t.join()
print("tamanho de pilha padrão (0 = o do sistema):", threading.stack_size())

# Disputa por uma trava: mais threads, o MESMO trabalho total
lock = threading.Lock()
counter = 0


def work(n):
    global counter
    for _ in range(n):
        with lock:
            counter += 1


print("1,6 milhão de incrementos protegidos por UMA trava:")
for workers in (1, 2, 4, 8, 16):
    counter = 0
    threads = [threading.Thread(target=work, args=(1_600_000 // workers,)) for _ in range(workers)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  {workers:>2} threads: {time.perf_counter() - start:.2f} s (counter = {counter:,})")
