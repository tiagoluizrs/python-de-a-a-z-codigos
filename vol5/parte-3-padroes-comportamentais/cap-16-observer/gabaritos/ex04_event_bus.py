"""Gabarito do exercício 4."""
from fnmatch import fnmatchcase


class EventBus:
    def __init__(self):
        self._subs = []
        self._errors = []
        self._history = []

    def subscribe(self, pattern, fn):
        if not callable(fn):
            raise TypeError("observador precisa ser chamável")
        if any(p == pattern and f == fn for p, f in self._subs):
            raise ValueError("já assinado")
        self._subs.append((pattern, fn))
        return fn

    def unsubscribe(self, pattern, fn):
        for i, (p, f) in enumerate(self._subs):
            if p == pattern and f == fn:
                del self._subs[i]
                return
        raise ValueError("não assinado")

    def subscribers(self, topic):
        return [f for p, f in self._subs if fnmatchcase(topic, p)]

    def publish(self, topic, payload=None):
        if not topic:
            raise ValueError("tópico vazio")
        self._history.append((topic, payload))
        ok = 0
        for fn in self.subscribers(topic):
            try:
                fn(topic, payload)
                ok += 1
            except Exception as error:
                self._errors.append((topic, getattr(fn, "__name__", repr(fn)), error))
        return ok

    @property
    def errors(self):
        return list(self._errors)

    @property
    def history(self):
        return list(self._history)
