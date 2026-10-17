"""Quanto custa uma abstração em Python? Quase nada comparado ao I/O, mas nem sempre nada."""
import sqlite3
import time
from dataclasses import dataclass
from typing import NamedTuple, Protocol


def best(fn, n, repeat=5):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        for _ in range(n):
            fn()
        out.append((time.perf_counter() - start) / n * 1e9)
    return min(out)


# 1. camadas de indireção: uma chamada direta contra N camadas que só repassam
def work(x):
    return x + 1


def layer1(x): return work(x)
def layer2(x): return layer1(x)
def layer3(x): return layer2(x)
def layer5(x): return layer3(layer2(x) - 1)


class Repo(Protocol):
    def get(self, x: int) -> int: ...


class RealRepo:
    def get(self, x):
        return x + 1


class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    def run(self, x):
        return self.repo.get(x)


service = Service(RealRepo())
N = 1_000_000
rows = [("chamada direta work(x)", best(lambda: work(1), N)),
        ("3 camadas que só repassam", best(lambda: layer3(1), N)),
        ("5 camadas", best(lambda: layer5(1), N)),
        ("Service(repo: Protocol).run(x)", best(lambda: service.run(1), N))]
base = rows[0][1]
print("custo de uma chamada (inclui o custo do lambda de medição):")
for label, ns in rows:
    print(f"  {label:<34} {ns:7.0f} ns  ({ns - base:+5.0f} ns sobre a chamada direta)")

# 2. o Protocol é de tipagem: em runtime, nenhum custo extra e nenhuma verificação
class Duck:
    def get(self, x):
        return x + 2


print("\nProtocol em runtime: Service(Duck()) funciona sem herdar de nada:", Service(Duck()).run(1), "| isinstance(Duck(), Repo) ->", end=" ")
try:
    isinstance(Duck(), Repo)
except TypeError as error:
    print("TypeError:", str(error)[:50], "(Protocol não verificável em runtime sem @runtime_checkable)")


# 3. objetos de domínio: dict, tupla nomeada, dataclass e dataclass com slots
@dataclass
class LineDC:
    sku: str
    qty: int
    price: float


@dataclass(slots=True)
class LineSlots:
    sku: str
    qty: int
    price: float


class LineNT(NamedTuple):
    sku: str
    qty: int
    price: float


M = 500_000
print(f"\ncriar um objeto de domínio ({M:,} vezes):")
for label, make in [("dict", lambda: {"sku": "A", "qty": 2, "price": 9.9}), ("NamedTuple", lambda: LineNT("A", 2, 9.9)),
                    ("dataclass", lambda: LineDC("A", 2, 9.9)), ("dataclass(slots=True)", lambda: LineSlots("A", 2, 9.9))]:
    print(f"  {label:<24} {best(make, M // 5, 3):7.0f} ns")
print("(modelar o domínio com objetos custa de 70 a 180 ns por objeto: irrelevante diante de qualquer I/O)")

# 4. o custo REAL que a arquitetura protege: I/O
conn = sqlite3.connect(":memory:")
conn.execute("create table t (id integer primary key, v integer)")
conn.executemany("insert into t values (?, ?)", [(i, i) for i in range(1000)])
t_query = best(lambda: conn.execute("select v from t where id = 500").fetchone(), 20_000, 3)
print(f"\numa consulta SQLite em memória por chave: {t_query:7.0f} ns ({t_query / rows[0][1]:.0f}x a chamada direta)")
print(f"5 camadas de indireção custam {rows[2][1] - base:.0f} ns; UMA consulta custa {t_query:.0f} ns; uma chamada de rede, milhões de ns")
print("conclusão: a indireção nunca é o gargalo; o custo está em I/O e em ler código com camadas demais")
