"""Gabarito do exercício 2."""
import time


def cpu_ratio(func, *args, clock=time.perf_counter, cpu_clock=time.process_time, **kwargs):
    wall_start, cpu_start = clock(), cpu_clock()
    result = func(*args, **kwargs)
    wall, cpu = clock() - wall_start, cpu_clock() - cpu_start
    return (cpu / wall if wall > 0 else 0.0), result


def classify(ratio, cpu_threshold=0.8, io_threshold=0.3):
    if ratio >= cpu_threshold:
        return "cpu"
    if ratio <= io_threshold:
        return "io"
    return "mixed"


def classify_function(func, *args, **kwargs):
    ratio, _ = cpu_ratio(func, *args, **kwargs)
    return classify(ratio), ratio
