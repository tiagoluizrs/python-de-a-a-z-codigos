"""Gabarito do exercício 3."""
import threading


class ShardedCounter:
    def __init__(self, shards=8):
        if shards < 1:
            raise ValueError("shards >= 1")
        self._shards = shards
        self._values = [0] * shards
        self._locks = [threading.Lock() for _ in range(shards)]

    def add(self, n=1):
        index = threading.get_ident() % self._shards
        with self._locks[index]:
            self._values[index] += n

    def total(self):
        total = 0
        for index in range(self._shards):
            with self._locks[index]:
                total += self._values[index]
        return total

    def reset(self):
        previous = 0
        for index in range(self._shards):
            with self._locks[index]:
                previous += self._values[index]
                self._values[index] = 0
        return previous
