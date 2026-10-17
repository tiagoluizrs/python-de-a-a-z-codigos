"""Gabarito do exercício 2."""


def speedup_table(sequential, timings):
    if sequential <= 0:
        raise ValueError("sequential > 0")
    rows = []
    for workers, elapsed in sorted(timings.items()):
        if workers < 1 or elapsed <= 0:
            raise ValueError("trabalhadores >= 1 e tempo > 0")
        speedup = sequential / elapsed
        rows.append((workers, speedup, speedup / workers))
    return rows


def best_workers(table, min_efficiency=0.5):
    best, best_speedup = 1, 0.0
    for workers, speedup, efficiency in sorted(table):
        if efficiency >= min_efficiency and speedup > best_speedup:
            best, best_speedup = workers, speedup
    return best
