"""Vazamentos típicos e diagnóstico com tracemalloc."""
import gc
import tracemalloc
import weakref

# ---- Vazamento 1: cache sem limite em variável global
_CACHE: dict[int, bytes] = {}


def handle_request(request_id: int) -> int:
    payload = bytes(10_000)
    _CACHE[request_id] = payload         # nunca é removido
    return len(payload)


tracemalloc.start()
gc.collect()
snap1 = tracemalloc.take_snapshot()

for i in range(500):
    handle_request(i)

gc.collect()
snap2 = tracemalloc.take_snapshot()
print("Maiores crescimentos (por linha):")
for stat in snap2.compare_to(snap1, "lineno")[:2]:
    frame = stat.traceback[0]
    print(f"  linha {frame.lineno}: +{stat.size_diff / 1024:.0f} KiB, "
          f"+{stat.count_diff} blocos")
tracemalloc.stop()


# ---- Vazamento 2: o traceback guarda o frame (e seus locais)
class Big:
    pass


def fails() -> None:
    big = Big()
    ref = weakref.ref(big)
    stash.append(ref)
    raise ValueError("boom")


stash: list[weakref.ref] = []
saved = None
try:
    fails()
except ValueError as exc:
    saved = exc                          # guarda a exceção
print("\nBig vive porque a exceção guarda o frame:", stash[0]() is not None)
saved.__traceback__ = None               # ou: del saved
gc.collect()
print("Big vive depois de soltar o traceback  :", stash[0]() is not None)

# O nome do `except ... as e` é apagado ao fim do bloco
try:
    raise KeyError("k")
except KeyError as err:
    pass
print("`err` existe depois do except?", "err" in globals())


# ---- Vazamento 3: closure que prende um objeto grande
def make_handler(blob: bytes):
    size = len(blob)

    def handler() -> int:
        return size + len(blob)          # usa blob: prende o objeto

    return handler


def make_handler_fixed(blob: bytes):
    size = len(blob)

    def handler() -> int:
        return size * 2                  # só o int fica na closure

    return handler


big = bytes(5_000_000)
bad, good = make_handler(big), make_handler_fixed(big)
print("\nclosure ruim tem cell com bytes:",
      any(isinstance(c.cell_contents, bytes)
          for c in bad.__closure__))
print("closure boa  tem cell com bytes:",
      any(isinstance(c.cell_contents, bytes)
          for c in good.__closure__))
