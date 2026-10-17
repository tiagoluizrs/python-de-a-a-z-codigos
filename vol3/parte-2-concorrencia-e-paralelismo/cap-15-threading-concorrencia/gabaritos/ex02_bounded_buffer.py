"""Gabarito do exercício 2."""
import collections
import queue
import threading
import time


class Closed(Exception):
    """O buffer foi fechado e está vazio."""


class BoundedBuffer:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity deve ser >= 1")
        self._capacity = capacity
        self._items = collections.deque()
        self._closed = False
        self._cond = threading.Condition()

    def _wait(self, predicate, timeout):
        return self._cond.wait_for(predicate, timeout=timeout)

    def put(self, item, timeout=None):
        with self._cond:
            if self._closed:
                raise Closed("buffer fechado")
            if not self._wait(lambda: self._closed or len(self._items) < self._capacity, timeout):
                raise queue.Full
            if self._closed:
                raise Closed("buffer fechado")
            self._items.append(item)
            self._cond.notify_all()

    def get(self, timeout=None):
        with self._cond:
            if not self._wait(lambda: self._items or self._closed, timeout):
                raise queue.Empty
            if not self._items:
                raise Closed("buffer fechado e vazio")
            item = self._items.popleft()
            self._cond.notify_all()
            return item

    def close(self):
        with self._cond:
            self._closed = True
            self._cond.notify_all()

    def __len__(self):
        with self._cond:
            return len(self._items)
