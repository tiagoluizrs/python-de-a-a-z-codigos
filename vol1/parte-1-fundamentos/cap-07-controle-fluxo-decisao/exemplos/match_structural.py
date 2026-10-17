"""Padrões estruturais: sequência, mapeamento, classe, aninhados."""
from dataclasses import dataclass


# --- Sequência
def seq(value):
    match value:
        case []:
            return "empty"
        case [x]:
            return f"one: {x}"
        case [x, y]:
            return f"two: {x}, {y}"
        case [first, *rest]:
            return f"first={first}, rest={rest}"
        case _:
            return "not a sequence"


print(seq([]), "|", seq((1,)), "|", seq([1, 2]), "|", seq("ab"))
print(seq(range(4)), "|", seq(5))
print(seq("abc"))          # str NÃO é tratada como sequência
print(seq({1, 2}), seq({"a": 1}))


def head_tail(items):
    match items:
        case [first, *_, last]:
            return first, last


print(head_tail([1, 2, 3, 4]), head_tail([9]))


# --- Mapeamento
def event(e):
    match e:
        case {"type": "click", "x": x, "y": y}:
            return f"click at {x},{y}"
        case {"type": "key", "key": str(k)}:
            return f"key {k}"
        case {"type": "scroll", **rest}:
            return f"scroll with {rest}"
        case _:
            return "unknown"


print(event({"type": "click", "x": 1, "y": 2, "extra": True}))
print(event({"type": "key", "key": "a"}))
print(event({"type": "key", "key": 1}))
print(event({"type": "scroll", "dy": 5, "dx": 0}))


# --- Classe
@dataclass
class Point:
    x: int
    y: int


def where(p):
    match p:
        case Point(x=0, y=0):
            return "origin"
        case Point(x=0, y=y):
            return f"on Y axis at {y}"
        case Point(x, 0):          # posicional via __match_args__
            return f"on X axis at {x}"
        case Point():
            return "somewhere"
        case _:
            return "not a point"


print(Point.__match_args__)
for p in (Point(0, 0), Point(0, 5), Point(3, 0), Point(1, 1), (1, 1)):
    print(where(p))


# Classe sem __match_args__: só argumentos nomeados
class Plain:
    def __init__(self, a):
        self.a = a


match Plain(7):
    case Plain(a=a):
        print("keyword ok", a)
try:
    match Plain(7):
        case Plain(a):
            pass
except TypeError as exc:
    print("TypeError:", exc)

# Tipos nativos aceitam um padrão posicional (o próprio valor)
match 3.5:
    case float(n):
        print("float", n)


# --- Aninhados
def line(shape):
    match shape:
        case ("line", Point(x=x1, y=y1), Point(x=x2, y=y2)):
            return f"line {x1},{y1} -> {x2},{y2}"
        case ("circle", Point() as c, int(r) | float(r)) if r > 0:
            return f"circle at {c} r={r}"
        case _:
            return "invalid"


print(line(("line", Point(0, 0), Point(2, 3))))
print(line(("circle", Point(1, 1), 2.5)))
print(line(("circle", Point(1, 1), -1)))
