"""Gabarito do exercício 3."""
from collections import deque


class Store:
    def __init__(self, update, state, limit=None):
        if limit is not None and limit < 1:
            raise ValueError("limite inválido")
        self.update, self.state = update, state
        self._past = deque(maxlen=limit)
        self._future = []                                    # o próximo a refazer fica no FIM
        self._subscribers = []

    def _notify(self):
        for fn in list(self._subscribers):
            fn(self.state)

    def dispatch(self, msg):
        new = self.update(self.state, msg)
        if new == self.state:
            return False
        self._past.append(self.state)
        self._future.clear()
        self.state = new
        self._notify()
        return True

    def subscribe(self, fn):
        self._subscribers.append(fn)

        def unsubscribe():
            if fn in self._subscribers:
                self._subscribers.remove(fn)

        return unsubscribe

    def undo(self):
        if not self._past:
            return False
        self._future.append(self.state)
        self.state = self._past.pop()
        self._notify()
        return True

    def redo(self):
        if not self._future:
            return False
        self._past.append(self.state)
        self.state = self._future.pop()
        self._notify()
        return True

    @property
    def can_undo(self):
        return bool(self._past)

    @property
    def can_redo(self):
        return bool(self._future)

    def timeline(self):
        return list(self._past) + [self.state] + list(reversed(self._future))

    @property
    def position(self):
        return len(self._past)

    def jump(self, index):
        line = self.timeline()
        if not 0 <= index < len(line):
            raise IndexError(f"posição inexistente: {index}")
        if index == self.position:
            return
        self._past = deque(line[:index], maxlen=self._past.maxlen)
        self._future = list(reversed(line[index + 1:]))
        self.state = line[index]
        self._notify()
