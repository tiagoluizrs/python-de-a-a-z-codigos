"""Gabarito do exercício 4."""
import signal
import threading
import time


class GracefulShutdown:
    def __init__(self):
        self._event = threading.Event()
        self._name = None
        self._previous = {}

    def _handler(self, signum, frame):
        if self._name is None:
            self._name = signal.Signals(signum).name
        self._event.set()

    def __enter__(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            self._previous[sig] = signal.signal(sig, self._handler)
        return self

    def __exit__(self, *exc):
        for sig, handler in self._previous.items():
            signal.signal(sig, handler)
        return False

    @property
    def requested(self):
        return self._event.is_set()

    @property
    def signal_name(self):
        return self._name

    def wait(self, timeout=None):
        return self._event.wait(timeout)


def serve(handle_one, shutdown, pending, grace_seconds=1.0):
    handled, late = 0, False
    requested_at = None
    while pending and not shutdown.requested:
        item = pending.pop(0)
        began = time.perf_counter()
        handle_one(item)
        handled += 1
        if shutdown.requested and requested_at is None:
            requested_at = began
            late = (time.perf_counter() - began) > grace_seconds
    return {"handled": handled, "left": len(pending), "reason": shutdown.signal_name if shutdown.requested else "done", "late": late}
