"""Armadilhas de match/case, com as mensagens reais."""
from enum import Enum


class Color(Enum):
    RED = 1
    GREEN = 2


RED_CODE = 10


def trap(value):
    match value:
        case RED_CODE:            # CAPTURA, não compara!
            return f"matched, RED_CODE is now {RED_CODE}"


print(trap(99))     # qualquer valor "casa" e RED_CODE muda!
print(RED_CODE)     # o global não foi tocado (aqui é local)


# Nome qualificado com ponto compara por ==:
class Codes:
    RED = 10


def right(value):
    match value:
        case Codes.RED:
            return "red"
        case Color.GREEN:
            return "green enum"
        case _:
            return "other"


print(right(10), right(Color.GREEN), right(99))

for source in (
    "match 1:\n    case RED_CODE:\n        pass\n    case 2:\n        pass",
    "match 1:\n    case x | 2:\n        pass",
    "match 1:\n    case (a, a):\n        pass",
):
    try:
        compile(source, "<demo>", "exec")
    except SyntaxError as exc:
        print("SyntaxError:", exc.msg)

# Captura sem ser a última também sobrescreve o nome
x = "antes"
match 5:
    case x:
        pass
print("x depois do match:", x)

# match e case continuam sendo nomes válidos
match = "texto"
case = len(match)
print(match, case)
import re
print(re.match("a", "abc") is not None)   # método match, nada a ver
