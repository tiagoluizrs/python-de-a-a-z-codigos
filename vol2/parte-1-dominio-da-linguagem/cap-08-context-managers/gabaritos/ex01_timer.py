"""Gabarito do exercício 1."""
import time


class Timer:
    def __init__(self, clock=time.perf_counter):
        self.clock = clock
        self.elapsed = None
        self.laps = []

    def __enter__(self):
        self._start = self.clock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = self.clock() - self._start      # roda mesmo com exceção
        self.laps.append(self.elapsed)
        return False                                    # não suprime
