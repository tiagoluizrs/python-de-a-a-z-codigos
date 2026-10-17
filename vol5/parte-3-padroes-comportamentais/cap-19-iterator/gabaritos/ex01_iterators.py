"""Gabarito do exercício 1."""


class CountdownIterator:
    def __init__(self, start):
        self._next = start

    def __iter__(self):
        return self

    def __next__(self):
        if self._next < 0:
            raise StopIteration
        value = self._next
        self._next -= 1
        return value


class Countdown:
    def __init__(self, start):
        if start < 0:
            raise ValueError("start negativo")
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)

    def __len__(self):
        return self.start + 1

    def __contains__(self, item):
        return isinstance(item, int) and not isinstance(item, bool) and 0 <= item <= self.start


class Fibonacci:
    def __init__(self, limit=None):
        if limit is not None and limit < 0:
            raise ValueError("limit negativo")
        self._limit, self._count = limit, 0
        self._a, self._b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        if self._limit is not None and self._count >= self._limit:
            raise StopIteration
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        self._count += 1
        return value


class PeekableIterator:
    _END = object()

    def __init__(self, iterable):
        self._it = iter(iterable)
        self._pushed = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._pushed:
            return self._pushed.pop()
        return next(self._it)

    def peek(self, *default):
        if not self._pushed:
            try:
                self._pushed.append(next(self._it))
            except StopIteration:
                if default:
                    return default[0]
                raise
        return self._pushed[-1]

    def has_next(self):
        return self.peek(self._END) is not self._END

    def push_back(self, value):
        self._pushed.append(value)
