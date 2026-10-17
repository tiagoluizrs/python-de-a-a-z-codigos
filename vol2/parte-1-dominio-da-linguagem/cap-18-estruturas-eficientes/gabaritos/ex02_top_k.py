"""Gabarito do exercício 2."""
import heapq


class TopK:
    def __init__(self, k):
        if k < 1:
            raise ValueError("k deve ser >= 1")
        self.k = k
        self._heap = []

    def add(self, value):
        if len(self._heap) < self.k:
            heapq.heappush(self._heap, value)
        elif value > self._heap[0]:
            heapq.heapreplace(self._heap, value)

    def result(self):
        return sorted(self._heap, reverse=True)

    def __len__(self):
        return len(self._heap)


def merge_sorted_streams(*streams):
    return list(heapq.merge(*streams))
