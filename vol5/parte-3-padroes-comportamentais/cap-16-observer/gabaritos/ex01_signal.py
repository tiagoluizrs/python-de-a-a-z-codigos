"""Gabarito do exercício 1."""


class Signal:
    def __init__(self):
        self._handlers = []                     # lista de [fn, once]

    def _index(self, fn):
        for i, (handler, _) in enumerate(self._handlers):
            if handler == fn:
                return i
        return -1

    def connect(self, fn=None, *, once=False):
        def register(function):
            if not callable(function):
                raise TypeError("observador precisa ser chamável")
            if self._index(function) >= 0:
                raise ValueError("já conectado")
            self._handlers.append((function, once))
            return function

        return register if fn is None else register(fn)

    def disconnect(self, fn):
        i = self._index(fn)
        if i < 0:
            raise ValueError("não conectado")
        del self._handlers[i]

    def emit(self, *args, **kwargs):
        errors, called = [], 0
        for handler, once in list(self._handlers):
            if once and self._index(handler) >= 0:
                self.disconnect(handler)
            try:
                handler(*args, **kwargs)
                called += 1
            except Exception as error:
                errors.append(error)
        if errors:
            raise ExceptionGroup("observadores falharam", errors)
        return called

    def __len__(self):
        return len(self._handlers)

    def __contains__(self, fn):
        return self._index(fn) >= 0
