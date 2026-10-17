"""Gabarito do exercício 3."""
import heapq


class RunningMedian:
    def __init__(self):
        self._low = []                 # max-heap (valores negados): metade menor
        self._high = []                # min-heap: metade maior

    def add(self, value):
        if self._low and value > -self._low[0]:
            heapq.heappush(self._high, value)
        else:
            heapq.heappush(self._low, -value)
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))
        elif len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def median(self):
        if not self._low:
            raise ValueError("sem valores")
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2
