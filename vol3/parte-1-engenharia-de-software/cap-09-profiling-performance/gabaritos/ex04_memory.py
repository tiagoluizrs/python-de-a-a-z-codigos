"""Gabarito do exercício 4."""
import gc
import os
import tracemalloc


def measure_peak(func, *args, **kwargs):
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    else:
        tracemalloc.reset_peak()
    try:
        result = func(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        if not was_tracing:
            tracemalloc.stop()
    return result, peak


def top_allocations(func, *args, limit=3, **kwargs):
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    try:
        keep = func(*args, **kwargs)
        snapshot = tracemalloc.take_snapshot()
    finally:
        if not was_tracing:
            tracemalloc.stop()
    snapshot = snapshot.filter_traces([tracemalloc.Filter(False, tracemalloc.__file__)])
    stats = snapshot.statistics("lineno")[:limit]
    del keep
    return [(f"{os.path.basename(s.traceback[0].filename)}:{s.traceback[0].lineno}", s.size) for s in stats]


def retains_memory(func, iterations=50, tolerance=2_000):
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    try:
        func()
        gc.collect()
        before = tracemalloc.get_traced_memory()[0]
        for _ in range(iterations):
            func()
        gc.collect()
        after = tracemalloc.get_traced_memory()[0]
    finally:
        if not was_tracing:
            tracemalloc.stop()
    return (after - before) / iterations > tolerance
