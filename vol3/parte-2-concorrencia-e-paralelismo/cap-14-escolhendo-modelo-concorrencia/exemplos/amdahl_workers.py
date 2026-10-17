"""Quanto ganhar com N trabalhadores: previsão (Amdahl) e medida."""
import time

import models
import tasks


def amdahl(parallel_fraction, workers):
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def job(parallel_items, serial_n):
    """Parte paralela: tarefas independentes. Parte serial: um passo que não divide (ex.: juntar resultados)."""
    items = [800_000] * parallel_items
    start = time.perf_counter()
    models.run_sequential(tasks.cpu_task, items)
    parallel_part = time.perf_counter() - start
    start = time.perf_counter()
    tasks.cpu_task(serial_n)
    serial_part = time.perf_counter() - start
    return parallel_part, serial_part, items


if __name__ == "__main__":
    parallel_part, serial_part, items = job(32, 4_000_000)
    total = parallel_part + serial_part
    p = parallel_part / total
    print(f"sequencial: paralelizável {parallel_part:.2f} s + serial {serial_part:.2f} s = {total:.2f} s  (p = {p:.0%})")
    print(f"{'trabalhadores':>14}{'previsto':>10}{'medido':>9}")
    for workers in (1, 2, 4, 8, 16):
        start = time.perf_counter()
        models.run_processes(tasks.cpu_task, items, workers)
        tasks.cpu_task(4_000_000)
        measured = total / (time.perf_counter() - start)
        print(f"{workers:>14}{amdahl(p, workers):>9.1f}x{measured:>8.1f}x")
    print(f"limite teórico com infinitos trabalhadores: {1 / (1 - p):.1f}x")
