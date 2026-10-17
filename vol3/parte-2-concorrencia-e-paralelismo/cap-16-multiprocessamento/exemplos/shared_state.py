"""Quando é preciso compartilhar: Value, SharedMemory e Manager (e seus custos)."""
import multiprocessing as mp
import time
from multiprocessing import shared_memory

import tasks

if __name__ == "__main__":
    value = mp.Value("i", 0)
    lock = mp.Lock()
    procs = [mp.Process(target=tasks.increment, args=(value, lock, 5_000)) for _ in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print("Value('i') com Lock, 4 processos x 5.000:", value.value)

    # SharedMemory: um bloco de bytes visível a todos, sem cópia
    block = shared_memory.SharedMemory(create=True, size=10_000_000)
    block.buf[:100] = bytes(range(100))
    with mp.Pool(2) as pool:
        print("SharedMemory (bloco de 10 MB) lido por 2 filhos:", pool.starmap(tasks.read_shared, [(block.name, 100)] * 2))
    block.close()
    block.unlink()                                  # sem unlink o bloco vaza

    # Manager: objetos "compartilhados" via um processo servidor (cada acesso é uma mensagem)
    with mp.Manager() as manager:
        shared = manager.dict()
        start = time.perf_counter()
        for i in range(2_000):
            shared[i] = i
        per_op = (time.perf_counter() - start) / 2_000
    local = {}
    start = time.perf_counter()
    for i in range(2_000):
        local[i] = i
    per_local = (time.perf_counter() - start) / 2_000
    print(f"escrita em dict: Manager {per_op * 1e6:.0f} us contra dict local {per_local * 1e9:.0f} ns ({per_op / per_local:,.0f}x mais lento)")
