"""Alternativas ao deepcopy: dataclasses.replace, reconstruir, pickle."""
import copy
import pickle
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Point:
    x: int
    y: int


p = Point(1, 2)
q = replace(p, y=5)          # nova instância com um campo trocado
print(p, q, p is q)


@dataclass
class Order:
    id: int
    lines: list[tuple[str, int]]


order = Order(1, [("pen", 2), ("book", 1)])

# replace faz cópia RASA: a lista é compartilhada
other = replace(order, id=2)
print("lines compartilhada:", other.lines is order.lines)

# Reconstrução explícita: copia só o que é mutável
rebuilt = Order(order.id, list(order.lines))
print("lines própria:", rebuilt.lines is not order.lines)
print("tuplas internas compartilhadas (ok, imutáveis):",
      rebuilt.lines[0] is order.lines[0])

# Roundtrip por pickle: cópia profunda, mas só de dados serializáveis
via_pickle = pickle.loads(pickle.dumps(order))
print("pickle:", via_pickle == order, via_pickle is not order)

# deepcopy aceita o que o pickle não aceita (lambda, por exemplo)
holder = {"fn": lambda: 1}
print("deepcopy de lambda:", copy.deepcopy(holder)["fn"]())
try:
    pickle.dumps(holder)
except Exception as exc:
    print(type(exc).__name__, "->", str(exc)[:60])
