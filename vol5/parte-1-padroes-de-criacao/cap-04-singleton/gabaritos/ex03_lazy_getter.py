"""Gabarito do exercício 3."""
import threading

_MISSING = object()


def make_getter(loader):
    lock = threading.Lock()
    state = {"value": _MISSING}

    def get():
        if state["value"] is _MISSING:
            with lock:
                if state["value"] is _MISSING:
                    state["value"] = loader()
        return state["value"]

    get.is_loaded = lambda: state["value"] is not _MISSING
    get.cache_clear = lambda: state.update(value=_MISSING)
    return get
