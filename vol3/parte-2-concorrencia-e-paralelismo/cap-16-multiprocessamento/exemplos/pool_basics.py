"""Pool: map, imap, imap_unordered, starmap, apply_async e o chunksize."""
import multiprocessing as mp
import time

import tasks

if __name__ == "__main__":
    with mp.Pool(4) as pool:
        print("map            :", pool.map(tasks.square, range(8)))
        print("starmap        :", pool.starmap(pow, [(2, 3), (3, 2), (10, 3)]))
        print("imap (ordem)   :", list(pool.imap(tasks.square, range(5))))
        print("imap_unordered :", sorted(pool.imap_unordered(tasks.square, range(5))), "(a ordem de chegada varia; aqui ordenado)")
        result = pool.apply_async(tasks.square, (12,))
        print("apply_async    :", result.get(timeout=5))

        # a exceção volta para o pai, com o traceback do filho como causa
        try:
            pool.map(tasks.fail, range(6))
        except ValueError as error:
            print("exceção do filho:", error, "| causa:", type(error.__cause__).__name__)

        # chunksize: o custo é por MENSAGEM, não por tarefa
        for label, kwargs in (("chunksize=1", {"chunksize": 1}), ("padrão", {}), ("chunksize=500", {"chunksize": 500})):
            start = time.perf_counter()
            pool.map(tasks.square, range(20_000), **kwargs)
            print(f"  20.000 tarefas minúsculas, {label:<14}: {(time.perf_counter() - start) * 1e3:7.1f} ms")

        # tarefas grandes: o chunksize quase não importa
        for chunksize in (1, 8):
            start = time.perf_counter()
            pool.map(tasks.cpu_sum, [300_000] * 32, chunksize=chunksize)
            print(f"  32 tarefas de ~4 ms, chunksize={chunksize}: {(time.perf_counter() - start) * 1e3:6.1f} ms")
