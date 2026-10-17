"""Lendo o campo ob_refcnt direto da memória (apenas para estudo)."""
import ctypes
import gc
import sys


def raw_refcnt(obj) -> int:
    # Os primeiros 8 bytes do objeto são ob_refcnt (build com GIL)
    return ctypes.c_ssize_t.from_address(id(obj)).value


data = [1, 2, 3]
print("ob_refcnt lido da memória:", raw_refcnt(data))
print("sys.getrefcount          :", sys.getrefcount(data))
other = data
print("com outro nome           :", raw_refcnt(data))
print("None é imortal?          :", sys._is_immortal(None))
print("lista é imortal?         :", sys._is_immortal(data))

# Observando coletas pelo callback do gc (3.15 informa duração)
events = []


def on_gc(phase: str, info: dict) -> None:
    if phase == "stop":
        events.append((info["generation"], info["collected"],
                       sorted(info)))


gc.callbacks.append(on_gc)
a = []
a.append(a)
del a
gc.collect()
gc.callbacks.remove(on_gc)
print("callback:", events[-1][:2], "chaves:", events[-1][2])
