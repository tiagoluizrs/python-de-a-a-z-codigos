"""Gabarito do exercício 2."""
import inspect
import weakref


class WeakSignal:
    def __init__(self):
        self._entries = []                      # WeakMethod ou a própria função

    @staticmethod
    def _resolve(entry):
        return entry() if isinstance(entry, weakref.WeakMethod) else entry

    def _find(self, fn):
        for i, entry in enumerate(self._entries):
            current = self._resolve(entry)
            if current is not None and current == fn:
                return i
        return -1

    def connect(self, fn):
        if not callable(fn):
            raise TypeError("observador precisa ser chamável")
        if self._find(fn) >= 0:
            raise ValueError("já conectado")
        self._entries.append(weakref.WeakMethod(fn) if inspect.ismethod(fn) else fn)
        return fn

    def disconnect(self, fn):
        i = self._find(fn)
        if i < 0:
            raise ValueError("não conectado")
        del self._entries[i]

    def emit(self, *args, **kwargs):
        called, first = 0, None
        alive = []
        for entry in list(self._entries):
            handler = self._resolve(entry)
            if handler is None:
                continue
            alive.append(entry)
            try:
                handler(*args, **kwargs)
                called += 1
            except Exception as error:
                first = first or error
        self._entries = alive
        if first is not None:
            raise first
        return called

    def __len__(self):
        return sum(1 for entry in self._entries if self._resolve(entry) is not None)
