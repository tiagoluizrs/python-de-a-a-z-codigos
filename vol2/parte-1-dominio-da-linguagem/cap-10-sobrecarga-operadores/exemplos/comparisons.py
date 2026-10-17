"""Comparações ricas, reflexão e total_ordering."""
import functools


class Version:
    def __init__(self, text):
        self.text = text
        self.parts = tuple(int(p) for p in text.split("."))

    def __repr__(self):
        return f"Version({self.text!r})"

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts

    def __hash__(self):
        return hash(self.parts)


v1, v2 = Version("1.9.0"), Version("1.10.0")
print(v1 < v2, sorted([v2, v1]), max(v1, v2))
print("só __lt__ definido: v1 > v2 usa o __lt__ refletido:", v2 > v1)
try:
    v1 <= v2
except TypeError as error:
    print("<= sem __le__:", error)
print(v1 == Version("1.9.0"), v1 != v2, v1 == "1.9.0")


# total_ordering completa os outros três a partir de __eq__ e UM operador
@functools.total_ordering
class Ordered(Version):
    pass


o1, o2 = Ordered("1.9.0"), Ordered("1.10.0")
print(o1 <= o2, o1 >= o2, o1 > o2)

# Comparações entre tipos que não sabem se comparar
try:
    v1 < 5
except TypeError as error:
    print("TypeError:", error)


# Reflexão de comparações: a < b tenta a.__lt__(b) e DEPOIS b.__gt__(a)
class Probe:
    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        print(f"  {self.name}.__lt__")
        return NotImplemented

    def __gt__(self, other):
        print(f"  {self.name}.__gt__")
        return True


print("Probe('a') < Probe('b'):")
print(" =", Probe("a") < Probe("b"))
