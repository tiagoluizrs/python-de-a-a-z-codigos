"""Gabarito do exercício 1."""


def _check(p, n):
    if not 0 <= p <= 1 or n < 1:
        raise ValueError("p em [0, 1] e n >= 1")


def amdahl_speedup(parallel_fraction, workers):
    _check(parallel_fraction, workers)
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def efficiency(parallel_fraction, workers):
    return amdahl_speedup(parallel_fraction, workers) / workers


def max_speedup(parallel_fraction):
    _check(parallel_fraction, 1)
    return float("inf") if parallel_fraction == 1 else 1 / (1 - parallel_fraction)


def gustafson_speedup(parallel_fraction, workers):
    _check(parallel_fraction, workers)
    return (1 - parallel_fraction) + parallel_fraction * workers


def best_worker_count(parallel_fraction, minimum_efficiency=0.5, limit=64):
    if parallel_fraction == 0:
        return 1
    best = 1
    for n in range(1, limit + 1):
        if efficiency(parallel_fraction, n) >= minimum_efficiency:
            best = n
    return best
