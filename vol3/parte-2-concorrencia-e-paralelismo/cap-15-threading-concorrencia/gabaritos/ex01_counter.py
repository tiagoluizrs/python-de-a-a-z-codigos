"""Gabarito do exercício 1."""
import threading


class SafeCounter:
    def __init__(self, start=0, on_step=None):
        self._value = start
        self._on_step = on_step
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    def add(self, n=1):
        with self._lock:
            current = self._value
            if self._on_step:
                self._on_step()
            self._value = current + n
            return self._value

    def compare_and_set(self, expected, new):
        with self._lock:
            if self._value == expected:
                self._value = new
                return True
            return False

    def update(self, func):
        with self._lock:
            self._value = func(self._value)
            return self._value
