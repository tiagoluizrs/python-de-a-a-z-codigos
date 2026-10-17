"""Gabarito do exercício 6."""
import time


class Timer:
    def __init__(self) -> None:
        self.elapsed_ns = 0
        self._start = 0

    def __enter__(self):
        self._start = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc, traceback):
        # Registra mesmo com exceção; devolver False a deixa propagar.
        self.elapsed_ns = time.perf_counter_ns() - self._start
        return False

    @property
    def elapsed(self) -> float:
        return self.elapsed_ns / 1e9
