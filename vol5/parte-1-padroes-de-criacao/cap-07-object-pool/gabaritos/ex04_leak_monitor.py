"""Gabarito do exercício 4."""


class LeaseMonitor:
    def __init__(self, clock):
        self._clock = clock
        self._open: dict[int, tuple[str, float]] = {}
        self._next = 1

    def acquired(self, label):
        token = self._next
        self._next += 1
        self._open[token] = (label, self._clock())
        return token

    def released(self, token):
        if token not in self._open:
            raise ValueError("token desconhecido")
        del self._open[token]

    @property
    def active(self):
        return len(self._open)

    def overdue(self, max_age):
        if max_age < 0:
            raise ValueError("max_age negativo")
        now = self._clock()
        late = [(label, now - started) for label, started in self._open.values() if now - started > max_age]
        return sorted(late, key=lambda item: (-item[1], item[0]))

    def report(self, max_age):
        late = self.overdue(max_age)
        if not late:
            return "sem vazamentos"
        return "\n".join(f"{label}: {age:.1f}s" for label, age in late)
