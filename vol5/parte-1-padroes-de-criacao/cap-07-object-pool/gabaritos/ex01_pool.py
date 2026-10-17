"""Gabarito do exercício 1."""
import collections
import contextlib
import threading
import time


class PoolExhausted(TimeoutError):
    pass


class Pool:
    def __init__(self, factory, size, *, reset=None, validate=None, close=None):
        if size < 1:
            raise ValueError("size deve ser >= 1")
        self._factory, self._size = factory, size
        self._reset, self._validate, self._close = reset, validate, close
        self._idle = collections.deque()
        self._leased: list = []
        self._created = 0
        self._discarded = 0
        self._closed = False
        self._cond = threading.Condition()

    def _drop(self, obj):
        self._created -= 1
        self._discarded += 1
        if self._close:
            self._close(obj)

    def acquire(self, timeout=None):
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._cond:
            while True:
                if self._closed:
                    raise RuntimeError("pool fechado")
                while self._idle:
                    obj = self._idle.popleft()
                    if self._validate is not None and not self._validate(obj):
                        self._drop(obj)
                        continue
                    self._leased.append(obj)
                    return obj
                if self._created < self._size:
                    self._created += 1
                    try:
                        obj = self._factory()
                    except BaseException:
                        self._created -= 1
                        raise
                    self._leased.append(obj)
                    return obj
                remaining = None if deadline is None else deadline - time.monotonic()
                if remaining is not None and remaining <= 0:
                    raise PoolExhausted(f"nenhum objeto livre em {timeout}s")
                self._cond.wait(remaining)

    def release(self, obj):
        with self._cond:
            for i, held in enumerate(self._leased):
                if held is obj:
                    del self._leased[i]
                    break
            else:
                raise ValueError("objeto não emprestado por este pool")
            try:
                if self._reset is not None:
                    self._reset(obj)
            except BaseException:
                self._drop(obj)
                self._cond.notify()
                raise
            if self._closed:
                self._drop(obj)
            else:
                self._idle.append(obj)
            self._cond.notify()

    @contextlib.contextmanager
    def lease(self, timeout=None):
        obj = self.acquire(timeout)
        try:
            yield obj
        finally:
            self.release(obj)

    def stats(self):
        with self._cond:
            return {"created": self._created, "idle": len(self._idle), "in_use": len(self._leased), "discarded": self._discarded}

    def close(self):
        with self._cond:
            self._closed = True
            while self._idle:
                obj = self._idle.popleft()
                if self._close:
                    self._close(obj)
            self._cond.notify_all()
