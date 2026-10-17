"""Gabarito do exercício 5."""
import gc
import weakref
from collections.abc import Callable


def release_mode(factory: Callable[[], object]) -> str:
    was_enabled = gc.isenabled()
    gc.disable()                    # sem coleta automática no meio do teste
    try:
        gc.collect()
        obj = factory()
        ref = weakref.ref(obj)
        del obj                     # solta o único nome forte
        if ref() is None:
            return "refcount"       # morreu na hora
        gc.collect()
        if ref() is None:
            return "gc"             # só o coletor cíclico resolveu
        return "never"
    finally:
        if was_enabled:
            gc.enable()
