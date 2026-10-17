"""Specification, forma clássica (GoF/DDD): uma regra de negócio vira um OBJETO que se combina com E, OU e NÃO."""
import ast
import inspect
import sqlite3
import textwrap
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    age: int
    country: str
    vip: bool = False
    banned: bool | None = False                              # None: "não sabemos" (NULL no banco)


USERS = [
    User(1, "Ana", 30, "BR"),
    User(2, "Bia", 17, "BR", vip=True),
    User(3, "Caio", 45, "PT", banned=True),
    User(4, "Duda", 22, "US", vip=True),
    User(5, "Edu", 19, "PT", banned=None),
    User(6, "Fabi", 18, "BR"),
]


# --- 1. o problema: a mesma regra copiada em vários lugares, cada cópia um pouco diferente ---
def eligible_naive(users):
    return [u for u in users if u.age >= 18 and (u.country in ("BR", "PT") or u.vip) and not u.banned]


def newsletter_naive(users):
    return [u for u in users if u.age >= 18 and not u.banned and (u.country == "BR" or u.vip)]       # esqueceu o "PT"


def report_naive(users):
    return [u for u in users if u.age >= 21 and u.country in ("BR", "PT")]                           # "maior de idade" virou 21


copies = sum(inspect.getsource(f).count("u.age >=") for f in (eligible_naive, newsletter_naive, report_naive))
print("a regra 'maior de idade' aparece", copies, "vezes, e as cópias já divergiram:",
      [u.name for u in eligible_naive(USERS)], "×", [u.name for u in newsletter_naive(USERS)], "(o Edu, de PT, sumiu da segunda) | cada combinação nova ('VIP e adulto e não banido') vira outra função")


# --- 2. a Specification: cada condição é um objeto; as combinações são dados ---
class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate): ...

    @abstractmethod
    def describe(self): ...

    def failures(self, candidate):
        """As condições (folhas) que explicam POR QUE o candidato não satisfaz a regra."""
        return [] if self.is_satisfied_by(candidate) else [self.describe()]

    def and_(self, other):
        return AndSpec(self, other)

    def or_(self, other):
        return OrSpec(self, other)

    def not_(self):
        return NotSpec(self)


class AgeAtLeast(Specification):
    def __init__(self, minimum):
        self.minimum = minimum

    def is_satisfied_by(self, user):
        return user.age >= self.minimum

    def describe(self):
        return f"idade >= {self.minimum}"

    def to_sql(self):
        return "age >= ?", (self.minimum,)


class FromCountry(Specification):
    def __init__(self, *codes):
        self.codes = codes

    def is_satisfied_by(self, user):
        return user.country in self.codes

    def describe(self):
        return f"país em {self.codes}"

    def to_sql(self):
        return f"country IN ({', '.join('?' * len(self.codes))})", tuple(self.codes)


class IsVip(Specification):
    def is_satisfied_by(self, user):
        return user.vip

    def describe(self):
        return "é VIP"

    def to_sql(self):
        return "vip = 1", ()


class IsBanned(Specification):
    def is_satisfied_by(self, user):
        return bool(user.banned)                             # None conta como "não banido"

    def describe(self):
        return "está banido"

    def to_sql(self):
        return "banned = 1", ()                              # ATENÇÃO: com banned NULL isto NÃO é falso, é desconhecido


class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate):
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def describe(self):
        return f"({self.left.describe()} E {self.right.describe()})"

    def failures(self, candidate):
        return self.left.failures(candidate) + self.right.failures(candidate)

    def to_sql(self):
        (lsql, lp), (rsql, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({lsql} AND {rsql})", lp + rp


class OrSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate):
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

    def describe(self):
        return f"({self.left.describe()} OU {self.right.describe()})"

    def failures(self, candidate):
        if self.is_satisfied_by(candidate):
            return []
        return self.left.failures(candidate) + self.right.failures(candidate)

    def to_sql(self):
        (lsql, lp), (rsql, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({lsql} OR {rsql})", lp + rp


class NotSpec(Specification):
    def __init__(self, inner):
        self.inner = inner

    def is_satisfied_by(self, candidate):
        return not self.inner.is_satisfied_by(candidate)

    def describe(self):
        return f"NÃO {self.inner.describe()}"

    def to_sql(self):
        sql, params = self.inner.to_sql()
        return f"(NOT {sql})", params


ELIGIBLE = AgeAtLeast(18).and_(FromCountry("BR", "PT").or_(IsVip())).and_(IsBanned().not_())
print("\nregra:", ELIGIBLE.describe())
print("elegíveis:", [u.name for u in USERS if ELIGIBLE.is_satisfied_by(u)])
for user in (USERS[1], USERS[2], User(0, "Zé", 16, "US", banned=True)):
    print(f"  {user.name}: por que não? {ELIGIBLE.failures(user)}")

# a mesma regra, reaproveitada: uma variação nova é uma COMBINAÇÃO, não uma função nova
NEWSLETTER = ELIGIBLE.and_(IsVip().not_())
print("newsletter (elegível e não VIP):", [u.name for u in USERS if NEWSLETTER.is_satisfied_by(u)], "| a regra 'maior de idade' continua escrita UMA vez")

# --- 3. a mesma regra vira SQL: uma regra, duas interpretações ---
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, country TEXT, vip INTEGER, banned INTEGER)")
conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", [(u.id, u.name, u.age, u.country, int(u.vip), None if u.banned is None else int(u.banned)) for u in USERS])


def ids_in_sql(spec):
    clause, params = spec.to_sql()
    return [row[0] for row in conn.execute(f"SELECT id FROM users WHERE {clause} ORDER BY id", params)]


in_memory = [u.id for u in USERS if ELIGIBLE.is_satisfied_by(u)]
print("\nem memória:", in_memory, "| em SQL:", ids_in_sql(ELIGIBLE), "(", ELIGIBLE.to_sql()[0], ")")
print("DIVERGÊNCIA: o Edu (id 5) tem banned = NULL. No Python, 'não está banido' é verdade; no SQL, NOT (NULL = 1) é NULL, e uma linha com NULL no WHERE é DESCARTADA")


class IsBannedNullSafe(IsBanned):
    def to_sql(self):
        return "COALESCE(banned, 0) = 1", ()                 # decide o que "desconhecido" significa: aqui, "não banido"


SAFE = AgeAtLeast(18).and_(FromCountry("BR", "PT").or_(IsVip())).and_(IsBannedNullSafe().not_())
print("com COALESCE: em memória", in_memory, "| em SQL", ids_in_sql(SAFE), "| a regra de NULL é uma DECISÃO de negócio, escrita na tradução")


# --- 4. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\numa regra inline:", measure([eligible_naive]), "| Specification (base + 4 folhas + 3 combinadores):", measure([Specification, AgeAtLeast, FromCountry, IsVip, IsBanned, AndSpec, OrSpec, NotSpec]))

BIG = USERS * 1_667                                          # ~10.000 candidatos


def ms(fn, n=20):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1000


print(f"filtrar {len(BIG)} usuários | comprehension inline {ms(lambda: eligible_naive(BIG)):5.2f} ms | árvore de Specification {ms(lambda: [u for u in BIG if ELIGIBLE.is_satisfied_by(u)]):5.2f} ms")
conn.close()
