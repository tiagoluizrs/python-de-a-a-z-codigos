"""Gabarito do exercício 1."""
import statistics
import time


class Timer:
    def __init__(self, clock_ns=time.perf_counter_ns):
        self._clock = clock_ns
        self._start = None
        self._end = None

    def __enter__(self):
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._end = self._clock()
        return False

    @property
    def elapsed_ns(self):
        end = self._end if self._end is not None else self._clock()
        return end - self._start

    @property
    def elapsed(self):
        return self.elapsed_ns / 1e9


def benchmark(func, *args, repeat=5, number=10, clock_ns=time.perf_counter_ns, **kwargs):
    if repeat < 1 or number < 1:
        raise ValueError("repeat e number devem ser >= 1")
    runs = []
    for _ in range(repeat):
        start = clock_ns()
        for _ in range(number):
            func(*args, **kwargs)
        runs.append((clock_ns() - start) / 1e9 / number)
    return {"min": min(runs), "median": statistics.median(runs), "mean": statistics.mean(runs),
            "stdev": statistics.stdev(runs) if repeat > 1 else 0.0, "runs": runs}
