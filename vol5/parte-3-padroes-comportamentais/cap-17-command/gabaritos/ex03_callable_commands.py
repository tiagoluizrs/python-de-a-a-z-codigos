"""Gabarito do exercício 3."""
import functools

_MISSING = object()


def make_set(store, key, value):
    saved = []

    def do():
        saved.append(store.get(key, _MISSING))
        store[key] = value

    def undo():
        if not saved:
            raise RuntimeError("comando não executado")
        old = saved.pop()
        if old is _MISSING:
            store.pop(key, None)
        else:
            store[key] = old

    return do, undo


def make_append(items, item):
    def do():
        items.append(item)

    def undo():
        if not items or items[-1] is not item:
            raise RuntimeError("lista alterada por fora")
        items.pop()

    return do, undo


def make_increment(counters, key, by=1):
    if by == 0:
        raise ValueError("incremento nulo")
    existed = []

    def do():
        existed.append(key in counters)
        counters[key] = counters.get(key, 0) + by

    def undo():
        counters[key] -= by
        if not existed.pop():
            del counters[key]

    return do, undo


class UndoStack:
    def __init__(self):
        self._pairs = []

    def do(self, pair):
        pair[0]()
        self._pairs.append(pair)

    def undo(self):
        if not self._pairs:
            return False
        self._pairs.pop()[1]()
        return True

    def undo_all(self):
        count, first = 0, None
        while self._pairs:
            pair = self._pairs.pop()
            try:
                pair[1]()
                count += 1
            except Exception as error:
                first = first or error
        if first:
            raise first
        return count

    def commit(self):
        count = len(self._pairs)
        self._pairs.clear()
        return count

    def __len__(self):
        return len(self._pairs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.undo_all()
        return False


class CommandQueue:
    def __init__(self):
        self._items = []

    def submit(self, fn, *args, **kwargs):
        if not callable(fn):
            raise TypeError("ação precisa ser chamável")
        self._items.append(functools.partial(fn, *args, **kwargs))
        return len(self._items) - 1

    def run_all(self):
        items, self._items = self._items, []
        results = []
        for action in items:
            try:
                results.append(action())
            except Exception as error:
                results.append(error)
        return results

    def clear(self):
        count = len(self._items)
        self._items.clear()
        return count

    def __len__(self):
        return len(self._items)
