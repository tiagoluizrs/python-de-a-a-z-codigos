"""Gabarito do exercício 6."""
from collections import deque


class EventBus:
    def __init__(self):
        self._subscriptions: list[tuple[type, object]] = []
        self._failures: list = []
        self._queue: deque = deque()
        self._draining = False

    def subscribe(self, event_type, handler):
        if (event_type, handler) not in self._subscriptions:
            self._subscriptions.append((event_type, handler))

    def unsubscribe(self, event_type, handler):
        if (event_type, handler) in self._subscriptions:
            self._subscriptions.remove((event_type, handler))

    def _dispatch(self, event):
        ok = 0
        for event_type, handler in list(self._subscriptions):
            if isinstance(event, event_type):
                try:
                    handler(event)
                    ok += 1
                except Exception as error:
                    self._failures.append((event, handler, error))
        return ok

    def _drain(self):
        if self._draining:
            return 0                                   # chamado de dentro de um handler: a fila atual vai tratar
        self._draining = True
        total = 0
        try:
            while self._queue:
                total += self._dispatch(self._queue.popleft())
        finally:
            self._draining = False
        return total

    def publish(self, event):
        self._queue.append(event)
        return self._drain()

    def publish_all(self, events):
        self._queue.extend(events)
        return self._drain()

    @property
    def failures(self):
        return list(self._failures)
