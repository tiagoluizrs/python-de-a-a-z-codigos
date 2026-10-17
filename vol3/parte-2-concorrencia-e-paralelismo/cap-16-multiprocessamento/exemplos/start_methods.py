"""Como um processo nasce: spawn, o guard de __main__ e o custo de partida."""
import multiprocessing as mp
import sys
import time

import tasks

if __name__ == "__main__":
    print("plataforma:", sys.platform, "| método padrão:", mp.get_start_method(), "| disponíveis:", mp.get_all_start_methods())
    print("CPUs:", mp.cpu_count())

    ctx = mp.get_context("spawn")
    times = []
    for _ in range(5):
        start = time.perf_counter()
        p = ctx.Process(target=tasks.square, args=(3,))
        p.start()
        p.join()
        times.append(time.perf_counter() - start)
    print(f"partir + terminar um processo (spawn): mediana {sorted(times)[2] * 1e3:.0f} ms")

    start = time.perf_counter()
    with ctx.Pool(4) as pool:
        pool.map(tasks.square, range(4))
    print(f"Pool(4) criado, usado uma vez e fechado: {(time.perf_counter() - start) * 1e3:.0f} ms")

    p = ctx.Process(target=tasks.pid)
    print("antes do start: pid =", p.pid, "| is_alive =", p.is_alive())
    p.start()
    p.join()
    print("depois do join: exitcode =", p.exitcode)
    print("Sem o guard de __main__, cada filho reimportaria este arquivo e tentaria criar outros filhos.")
