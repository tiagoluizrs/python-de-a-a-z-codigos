"""Gabarito do exercício 6."""
from collections import defaultdict


class TumblingWindows:
    def __init__(self, size, lateness=0):
        if size < 1 or lateness < 0:
            raise ValueError("size >= 1 e lateness >= 0")
        self.size, self.lateness = size, lateness
        self._open: dict[int, dict[str, float]] = {}
        self._max_ts = None
        self._dropped = 0

    def _watermark(self):
        return None if self._max_ts is None else self._max_ts - self.lateness

    def _close(self, up_to):
        closed = []
        for start in sorted(w for w in self._open if w + self.size <= up_to):
            closed += [(start, key, total) for key, total in sorted(self._open.pop(start).items())]
        return closed

    def add(self, ts, key, value=1.0):
        if ts < 0:
            raise ValueError("ts negativo")
        start = ts // self.size * self.size
        before = self._watermark()
        late = before is not None and start + self.size <= before
        self._max_ts = ts if self._max_ts is None else max(self._max_ts, ts)
        if late:
            self._dropped += 1
        else:
            self._open.setdefault(start, defaultdict(float))[key] += value
        return self._close(self._watermark())

    def flush(self):
        return self._close(float("inf"))

    @property
    def open_windows(self):
        return len(self._open)

    @property
    def dropped(self):
        return self._dropped


def batch_totals(events, size):
    totals = defaultdict(float)
    for ts, key, value in events:
        totals[(ts // size * size, key)] += value
    return dict(totals)
