"""Gabarito do exercício 3."""
import time


def best_time(func, repeat: int = 5) -> float:
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    # O menor tempo é o menos afetado por ruído do sistema operacional
    return min(times)
