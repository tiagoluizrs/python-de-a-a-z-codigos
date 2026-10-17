"""__slots__ e a diferença entre tamanho raso e tamanho profundo."""
import sys
import tracemalloc
from dataclasses import dataclass


class Plain:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass(slots=True)
class DC:
    x: int
    y: int


p, s = Plain(1, 2), Slotted(1, 2)
print("getsizeof Plain  :", sys.getsizeof(p))
print("getsizeof Slotted:", sys.getsizeof(s))
print("Plain tem __dict__ :", hasattr(p, "__dict__"))
print("Slotted tem __dict__:", hasattr(s, "__dict__"))


def measure(factory, n: int = 200_000) -> float:
    tracemalloc.start()
    objs = [factory(i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs
    return current / n


# Valores grandes e distintos, para não confundir com o cache de ints
for label, factory in (
    ("Plain", lambda i: Plain(i + 10**6, i + 2 * 10**6)),
    ("Slotted", lambda i: Slotted(i + 10**6, i + 2 * 10**6)),
    ("dataclass(slots=True)", lambda i: DC(i + 10**6, i + 2 * 10**6)),
):
    print(f"{label:<22} {measure(factory):6.1f} bytes por instância")


# Tamanho raso x profundo
def deep_size(obj, seen=None) -> int:
    seen = set() if seen is None else seen
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen)
                    for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_size(i, seen) for i in obj)
    elif hasattr(obj, "__dict__"):
        size += deep_size(vars(obj), seen)
    return size


record = {"name": "x" * 100, "values": list(range(1000, 1100))}
print("\ngetsizeof :", sys.getsizeof(record))
print("deep_size :", deep_size(record))
