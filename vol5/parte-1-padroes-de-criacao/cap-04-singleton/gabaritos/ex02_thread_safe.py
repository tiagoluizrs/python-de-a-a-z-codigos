"""Gabarito do exercício 2."""
import threading


def singleton(cls):
    lock = threading.Lock()
    state = {"instance": None, "created": 0}
    original_new = cls.__new__
    original_init = cls.__init__

    def __new__(klass, *args, **kwargs):
        if state["instance"] is None:
            with lock:
                if state["instance"] is None:
                    instance = object.__new__(klass) if original_new is object.__new__ else original_new(klass, *args, **kwargs)
                    original_init(instance, *args, **kwargs)
                    state["instance"] = instance
                    state["created"] += 1
        return state["instance"]

    def __init__(self, *args, **kwargs):
        pass

    cls.__new__ = __new__
    cls.__init__ = __init__
    cls.reset_singleton = staticmethod(lambda: state.update(instance=None))
    cls.singleton_created = staticmethod(lambda: state["created"])
    return cls
