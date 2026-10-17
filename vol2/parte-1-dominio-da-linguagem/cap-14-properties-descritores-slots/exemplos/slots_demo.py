"""__slots__: instâncias sem __dict__, com campos fixos."""
import sys
import tracemalloc
import weakref


class Plain:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


p, s = Plain(1, 2), Slotted(1, 2)
print(hasattr(p, "__dict__"), hasattr(s, "__dict__"))
print(vars(p))
print(type(Slotted.__dict__["x"]).__name__, Slotted.x)
try:
    s.z = 3
except AttributeError as error:
    print("AttributeError:", error)
try:
    vars(s)
except TypeError as error:
    print("TypeError:", error)
p.z = 3                                          # a classe comum aceita qualquer atributo
print(sorted(vars(p)))

# Memória em escala
def traced(factory, n=100_000):
    tracemalloc.start()
    kept = [factory(i, i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current / 1e6


plain_mb, slots_mb = traced(Plain), traced(Slotted)
print(f"100 mil objetos: comum {plain_mb:.1f} MB | __slots__ {slots_mb:.1f} MB "
      f"({plain_mb / slots_mb:.2f}x)")
print(sys.getsizeof(p), sys.getsizeof(s))

# weakref exige declarar __weakref__
try:
    weakref.ref(s)
except TypeError as error:
    print("TypeError:", error)


class WeakSlotted:
    __slots__ = ("x", "__weakref__")


print(weakref.ref(WeakSlotted()) is not None)


# Herança: a subclasse sem __slots__ ganha __dict__ de volta
class Child(Slotted):
    pass


c = Child(1, 2)
c.extra = 1
print("Child tem __dict__:", hasattr(c, "__dict__"))


class SlottedChild(Slotted):
    __slots__ = ("z",)                           # só o novo; x e y vêm da base


print(hasattr(SlottedChild(1, 2), "__dict__"))

# Conflitos
try:
    class Conflict:
        __slots__ = ("x",)
        x = 5                                    # valor padrão na classe: conflito
except ValueError as error:
    print("ValueError:", error)

class A:
    __slots__ = ("a",)

class B:
    __slots__ = ("b",)

try:
    class Both(A, B):
        pass
except TypeError as error:
    print("TypeError:", error)
