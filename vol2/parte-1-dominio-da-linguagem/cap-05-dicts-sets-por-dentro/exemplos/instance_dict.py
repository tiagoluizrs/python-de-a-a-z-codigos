"""O dict de instância, __slots__ e o custo por objeto."""
import sys
import tracemalloc


class Plain:
    def __init__(self):
        self.a, self.b, self.c = 1, 2, 3


class Slotted:
    __slots__ = ("a", "b", "c")

    def __init__(self):
        self.a, self.b, self.c = 1, 2, 3


obj = Plain()
print("instância:", sys.getsizeof(obj))
print("__dict__ materializado:", sys.getsizeof(obj.__dict__))
print("dict literal igual   :", sys.getsizeof({"a": 1, "b": 2, "c": 3}))
print("instância com slots  :", sys.getsizeof(Slotted()))


def traced(factory, n=100_000):
    tracemalloc.start()
    kept = [factory() for _ in range(n)]
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current / 1e6, kept


for name, factory in (("instâncias", Plain),
                      ("dicts", lambda: {"a": 1, "b": 2, "c": 3}),
                      ("com __slots__", Slotted)):
    megabytes, _kept = traced(factory)
    print(f"100 mil {name:<14}: {megabytes:5.1f} MB")
