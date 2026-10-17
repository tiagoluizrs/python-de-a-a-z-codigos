"""Gabarito do exercício 4."""
import multiprocessing as mp

import tasks


def count_with_processes(processes, per_process):
    if processes < 1 or per_process < 0:
        raise ValueError("processes >= 1 e per_process >= 0")
    ctx = mp.get_context("spawn")
    value = ctx.Value("i", 0)
    lock = ctx.Lock()
    procs = [ctx.Process(target=tasks.increment, args=(value, lock, per_process)) for _ in range(processes)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return value.value
