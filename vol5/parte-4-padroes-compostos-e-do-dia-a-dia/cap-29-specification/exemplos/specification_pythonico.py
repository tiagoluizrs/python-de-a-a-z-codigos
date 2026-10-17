"""Specification em Python: predicados e combinadores, operadores &, | e ~, e um DSL de campos que vira função E SQL (com a lógica de três valores do NULL)."""
import operator
import sqlite3
import time
from dataclasses import dataclass
from functools import partial

ROWS = [
    {"id": 1, "name": "Ana", "age": 30, "country": "BR", "vip": 0, "banned": 0},
    {"id": 2, "name": "Bia", "age": 17, "country": "BR", "vip": 1, "banned": 0},
    {"id": 3, "name": "Caio", "age": 45, "country": "PT", "vip": 0, "banned": 1},
    {"id": 4, "name": "Duda", "age": 22, "country": "US", "vip": 1, "banned": 0},
    {"id": 5, "name": "Edu", "age": 19, "country": "PT", "vip": 0, "banned": None},      # banned DESCONHECIDO
    {"id": 6, "name": "Fabi", "age": 18, "country": "BR", "vip": 0, "banned": 0},
    {"id": 7, "name": "Gil", "age": None, "country": "BR", "vip": 1, "banned": 0},       # idade DESCONHECIDA
]


# --- 1. uma Specification é só um predicado: funções + combinadores ---
def all_of(*predicates):
    return lambda item: all(p(item) for p in predicates)


def any_of(*predicates):
    return lambda item: any(p(item) for p in predicates)


def negate(predicate):
    return lambda item: not predicate(item)


def older_than(minimum, row):
    return (row["age"] or 0) >= minimum


adult = partial(older_than, 18)                              # functools.partial: "maior de idade" é uma função com o 18 preso
from_br_or_pt = lambda row: row["country"] in ("BR", "PT")
is_vip = lambda row: bool(row["vip"])
not_banned = negate(lambda row: bool(row["banned"]))
eligible = all_of(adult, any_of(from_br_or_pt, is_vip), not_banned)
print("funções + combinadores:", [r["name"] for r in filter(eligible, ROWS)], "| 'filter' recebe a regra pronta; uma variação é outra combinação")


# --- 2. os operadores &, | e ~ ---
class Spec:
    def __init__(self, fn, description="?"):
        self.fn, self.description = fn, description

    def __call__(self, item):
        return self.fn(item)

    def __and__(self, other):
        return Spec(lambda item: self(item) and other(item), f"({self.description} e {other.description})")

    def __or__(self, other):
        return Spec(lambda item: self(item) or other(item), f"({self.description} ou {other.description})")

    def __invert__(self):
        return Spec(lambda item: not self(item), f"não {self.description}")

    def __repr__(self):
        return self.description


def spec(description):
    return lambda fn: Spec(fn, description)


@spec("maior de idade")
def adult_s(row):
    return (row["age"] or 0) >= 18


@spec("do BR ou PT")
def local_s(row):
    return row["country"] in ("BR", "PT")


@spec("VIP")
def vip_s(row):
    return bool(row["vip"])


@spec("banido")
def banned_s(row):
    return bool(row["banned"])


rule = adult_s & (local_s | vip_s) & ~banned_s
print("\noperadores:", rule, "->", [r["name"] for r in ROWS if rule(r)])


# --- 3. o DSL de campos: F.idade >= 18 vira uma regra E um trecho de SQL ---
COLUMNS = {"id", "name", "age", "country", "vip", "banned"}               # a lista de permissão: só estes nomes viram SQL


class Spec3:
    """Lógica de TRÊS valores (True, False, None = desconhecido), como o SQL: é o que faz a regra em Python e a regra em SQL darem o MESMO resultado."""

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)

    def __call__(self, row):
        return self.evaluate(row) is True                    # desconhecido NÃO satisfaz, como uma linha com NULL no WHERE


OPS = {"==": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
SQL_OPS = {"==": "=", "!=": "<>"}


@dataclass(frozen=True)
class Cmp(Spec3):
    column: str
    op: str
    value: object

    def evaluate(self, row):
        actual = row.get(self.column)
        return None if actual is None else OPS[self.op](actual, self.value)

    def to_sql(self):
        return f"{self.column} {SQL_OPS.get(self.op, self.op)} ?", (self.value,)

    def __repr__(self):
        return f"{self.column} {self.op} {self.value!r}"


@dataclass(frozen=True)
class And(Spec3):
    left: Spec3
    right: Spec3

    def evaluate(self, row):
        a, b = self.left.evaluate(row), self.right.evaluate(row)
        if a is False or b is False:
            return False
        return None if a is None or b is None else True

    def to_sql(self):
        (ls, lp), (rs, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({ls} AND {rs})", lp + rp

    def __repr__(self):
        return f"({self.left!r} e {self.right!r})"


@dataclass(frozen=True)
class Or(Spec3):
    left: Spec3
    right: Spec3

    def evaluate(self, row):
        a, b = self.left.evaluate(row), self.right.evaluate(row)
        if a is True or b is True:
            return True
        return None if a is None or b is None else False

    def to_sql(self):
        (ls, lp), (rs, rp) = self.left.to_sql(), self.right.to_sql()
        return f"({ls} OR {rs})", lp + rp

    def __repr__(self):
        return f"({self.left!r} ou {self.right!r})"


@dataclass(frozen=True)
class Not(Spec3):
    inner: Spec3

    def evaluate(self, row):
        value = self.inner.evaluate(row)
        return None if value is None else not value

    def to_sql(self):
        sql, params = self.inner.to_sql()
        return f"(NOT {sql})", params

    def __repr__(self):
        return f"não {self.inner!r}"


class Field:
    def __init__(self, name):
        if name not in COLUMNS:
            raise AttributeError(f"coluna desconhecida: {name}")
        self.name = name

    def __eq__(self, value):                                  # F.x == 3 devolve uma regra, e não um bool
        return Cmp(self.name, "==", value)

    def __ne__(self, value):
        return Cmp(self.name, "!=", value)

    def __lt__(self, value):
        return Cmp(self.name, "<", value)

    def __le__(self, value):
        return Cmp(self.name, "<=", value)

    def __gt__(self, value):
        return Cmp(self.name, ">", value)

    def __ge__(self, value):
        return Cmp(self.name, ">=", value)

    __hash__ = None                                           # __eq__ mudou de significado: o Field deixa de ser "hashable"

    def isin(self, values):
        options = [Cmp(self.name, "==", v) for v in values]
        if not options:
            raise ValueError("isin precisa de pelo menos um valor")          # 'IN ()' não é SQL válido
        result = options[0]
        for other in options[1:]:
            result = Or(result, other)
        return result


class _F:
    def __getattr__(self, name):
        return Field(name)


F = _F()

dsl_rule = (F.age >= 18) & (F.country.isin(["BR", "PT"]) | (F.vip == 1)) & ~(F.banned == 1)
print("\nDSL:", dsl_rule)
print("em Python:", [r["name"] for r in ROWS if dsl_rule(r)])

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, country TEXT, vip INTEGER, banned INTEGER)")
conn.executemany("INSERT INTO users VALUES (:id, :name, :age, :country, :vip, :banned)", ROWS)
clause, params = dsl_rule.to_sql()
in_sql = [name for (name,) in conn.execute(f"SELECT name FROM users WHERE {clause} ORDER BY id", params)]
print("em SQL:    ", in_sql, "|", clause, params)
assert [r["name"] for r in ROWS if dsl_rule(r)] == in_sql
try:
    F.senha
except AttributeError as error:
    print("coluna fora da lista de permissão:", error, "(nenhum nome vindo de fora vira SQL sem passar por aqui)")

# a prova: várias regras, TODAS as linhas (inclusive as com NULL), Python e SQL concordam
checks = [~(F.banned == 1), ~(F.age >= 18), (F.age < 20) | (F.banned == 1), ~((F.age >= 18) & (F.banned == 0)), F.country.isin(["US", "PT"]) & ~(F.vip == 1)]
agree = []
for check in checks:
    sql, p = check.to_sql()
    agree.append([r["id"] for r in ROWS if check(r)] == [i for (i,) in conn.execute(f"SELECT id FROM users WHERE {sql} ORDER BY id", p)])
print("Python e SQL concordam em", sum(agree), "de", len(agree), "regras (com NULL em age e banned)")


# --- 4. a explicação: por que NÃO? ---
def why_not(spec_, row):
    match spec_:
        case And(left, right):
            return why_not(left, row) + why_not(right, row)
        case Or(left, right):
            return [] if spec_(row) else why_not(left, row) + why_not(right, row)
        case Not():
            return [] if spec_(row) else [repr(spec_)]
        case Cmp():
            if spec_.evaluate(row) is True:
                return []
            return [repr(spec_) + (" (valor ausente)" if row.get(spec_.column) is None else "")]
    return []


print("\npor que o Bia, o Caio e o Gil ficaram de fora?")
for r in (ROWS[1], ROWS[2], ROWS[6]):
    print(f"  {r['name']:5}", why_not(dsl_rule, r))


# --- 5. o custo ---
BIG = ROWS * 1_429                                            # ~10.000 linhas


def ms(fn, n=10):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1000


inline = lambda: [r for r in BIG if (r["age"] or 0) >= 18 and (r["country"] in ("BR", "PT") or r["vip"]) and not r["banned"]]
print(f"\nfiltrar {len(BIG)} linhas | inline {ms(inline):5.2f} ms | combinadores de funções {ms(lambda: [r for r in BIG if eligible(r)]):5.2f} ms | operadores & | ~ {ms(lambda: [r for r in BIG if rule(r)]):5.2f} ms | DSL de 3 valores {ms(lambda: [r for r in BIG if dsl_rule(r)]):5.2f} ms")
conn.close()
