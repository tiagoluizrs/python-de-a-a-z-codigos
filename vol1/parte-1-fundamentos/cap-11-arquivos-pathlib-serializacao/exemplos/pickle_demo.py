"""pickle: como funciona, o que ele NÃO guarda e por que é perigoso.

O "ataque" abaixo é inofensivo: só chama print. O ponto é mostrar que
carregar um pickle executa código escolhido por quem o criou.
"""
import io
import pickle
import pickletools
import threading
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


# --- ida e volta
data = {"points": [Point(1, 2), Point(3, 4)], "tags": {"a", "b"},
        "when": (2026, 10, 12), "raw": b"\x00\xff"}
blob = pickle.dumps(data)
print(len(blob), "bytes, protocolo padrão", pickle.DEFAULT_PROTOCOL)
back = pickle.loads(blob)
print(back == data, back["when"])    # tupla continua tupla

# --- o fluxo é um programa para uma "máquina de pilha"
pickletools.dis(pickle.dumps(Point(1, 2), protocol=2))

# --- o que não dá para serializar
for obj in (lambda x: x, threading.Lock()):
    try:
        pickle.dumps(obj)
    except (pickle.PicklingError, TypeError, AttributeError) as exc:
        print(type(exc).__name__)


# --- RISCO: __reduce__ diz ao pickle "para reconstruir, chame isto"
class Harmless:
    def __reduce__(self):
        # Um atacante poderia pôr aqui qualquer chamável, como
        # os.system. Usamos print para a demonstração.
        return (print, ("[!] código executado no loads()",))


evil = pickle.dumps(Harmless())
print("antes do loads")
pickle.loads(evil)                   # imprime a mensagem acima
print("depois do loads")

# --- defesa parcial: Unpickler que só aceita classes de uma lista
ALLOWED = {("builtins", "dict"), ("builtins", "list"),
           (__name__, "Point")}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"blocked: {module}.{name}")


def safe_loads(blob):
    return RestrictedUnpickler(io.BytesIO(blob)).load()


print(safe_loads(pickle.dumps([Point(1, 2)])))
try:
    safe_loads(evil)
except pickle.UnpicklingError as exc:
    print("UnpicklingError:", exc)
