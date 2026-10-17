"""Gabarito do exercício 4."""
import queue
import threading


class Handle:
    def __init__(self):
        self._event = threading.Event()
        self._value = None
        self._error = None

    def _set(self, value=None, error=None):
        self._value, self._error = value, error
        self._event.set()

    def done(self):
        return self._event.is_set()

    def result(self, timeout=None):
        if not self._event.wait(timeout):
            raise TimeoutError("tarefa não terminou")
        if self._error is not None:
            raise self._error
        return self._value


class WorkerPool:
    def __init__(self, workers):
        if workers < 1:
            raise ValueError("workers >= 1")
        self._queue = queue.Queue()
        self._closed = False
        self._lock = threading.Lock()
        self.threads = [threading.Thread(target=self._run, name=f"pool-{i}") for i in range(workers)]
        for thread in self.threads:
            thread.start()

    def _run(self):
        while (job := self._queue.get()) is not None:
            handle, func, args, kwargs = job
            try:
                handle._set(value=func(*args, **kwargs))
            except BaseException as error:        # noqa: BLE001
                handle._set(error=error)

    def submit(self, func, *args, **kwargs):
        with self._lock:
            if self._closed:
                raise RuntimeError("pool encerrado")
            handle = Handle()
            self._queue.put((handle, func, args, kwargs))
            return handle

    def shutdown(self, wait=True):
        with self._lock:
            if not self._closed:
                self._closed = True
                for _ in self.threads:
                    self._queue.put(None)
        if wait:
            for thread in self.threads:
                thread.join()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.shutdown(wait=True)
        return False
