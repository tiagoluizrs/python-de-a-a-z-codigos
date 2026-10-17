"""Builder em Python: argumentos nomeados, dataclasses e, quando há passos de verdade, um builder IMUTÁVEL."""
import ast
import email.message
import inspect
import textwrap
import time
from dataclasses import dataclass, field, replace
from typing import Self


# --- 1. o construtor com argumentos nomeados resolve o construtor telescópico ---
@dataclass(frozen=True, kw_only=True)
class Pizza:
    size: str
    dough: str = "tradicional"
    toppings: tuple = ()
    extra_sauce: bool = False

    def __post_init__(self):                                 # a validação mora no próprio objeto: vale para QUALQUER caminho de criação
        if len(self.toppings) > 5:
            raise ValueError("no máximo 5 ingredientes")


pizza = Pizza(size="large", toppings=("queijo", "cogumelo"), extra_sauce=True)
print("argumentos nomeados:", pizza)
try:
    Pizza(size="large", toppings=tuple("abcdef"))
except ValueError as error:
    print("validação no __post_init__:", error)
try:
    Pizza("large")                                           # type: ignore[misc]
except TypeError as error:
    print("kw_only impede a chamada que não se lê:", error)

# --- 2. variantes: dataclasses.replace (o 'builder' de uma linha) ---
margherita = Pizza(size="medium", dough="fina", toppings=("queijo", "manjericão"))
big = replace(margherita, size="large")
print("\nreplace cria uma variante sem tocar no original:", big.size, "|", margherita.size)


# --- 3. quando HÁ passos de verdade: um builder imutável (cada passo devolve um objeto NOVO) ---
@dataclass(frozen=True)
class Query:
    """Monta um SELECT parametrizado. Cada método devolve uma NOVA consulta: a base pode ser reutilizada sem vazar estado."""
    table: str
    columns: tuple = ("*",)
    conditions: tuple = ()
    params: tuple = ()
    order: tuple = ()
    max_rows: int | None = None

    ALLOWED = {"users": {"id", "name", "age", "city"}}

    def select(self, *columns: str) -> Self:
        self._check(columns)
        return replace(self, columns=columns)

    def where(self, column: str, op: str, value) -> Self:
        self._check([column])
        if op not in ("=", "<", ">", "<=", ">=", "!="):
            raise ValueError(f"operador inválido: {op}")
        return replace(self, conditions=self.conditions + (f"{column} {op} ?",), params=self.params + (value,))

    def order_by(self, column: str, descending: bool = False) -> Self:
        self._check([column])
        return replace(self, order=self.order + (f"{column} {'DESC' if descending else 'ASC'}",))

    def limit(self, n: int) -> Self:
        return replace(self, max_rows=int(n))

    def _check(self, columns):
        allowed = self.ALLOWED[self.table]
        for c in columns:
            if c != "*" and c not in allowed:
                raise ValueError(f"coluna desconhecida: {c}")

    def build(self) -> tuple[str, tuple]:
        sql = f"SELECT {', '.join(self.columns)} FROM {self.table}"
        if self.conditions:
            sql += " WHERE " + " AND ".join(self.conditions)
        if self.order:
            sql += " ORDER BY " + ", ".join(self.order)
        if self.max_rows is not None:
            sql += f" LIMIT {self.max_rows}"
        return sql, self.params


base = Query("users").select("id", "name").where("age", ">", 18)
adults_sp = base.where("city", "=", "SP").order_by("name").limit(10)
adults_rj = base.where("city", "=", "RJ")
print("\nbuilder imutável (a base é reaproveitada sem vazar estado):")
print(" ", adults_sp.build())
print(" ", adults_rj.build())
print("  a base continua intacta:", base.build())
try:
    Query("users").where("age; DROP TABLE users", "=", 1)
except ValueError as error:
    print("os NOMES passam por uma lista de permissão e os VALORES vão como parâmetros:", error)


# --- 4. o contraste: o builder MUTÁVEL vaza estado quando a base é reaproveitada ---
class MutableBuilder:
    def __init__(self):
        self.toppings = []

    def topping(self, name):
        self.toppings.append(name)
        return self

    def build(self):
        return tuple(self.toppings)


shared = MutableBuilder().topping("queijo")
a = shared.topping("cebola").build()
b = shared.topping("azeitona").build()
print("\nbuilder mutável reaproveitado:", a, b, "(o segundo herdou a cebola: bug clássico)")

# --- 5. a biblioteca padrão já tem builders ---
msg = email.message.EmailMessage()
msg["To"] = "ana@exemplo.com"
msg["Subject"] = "Olá"
msg.set_content("corpo do e-mail")
msg.add_alternative("<p>corpo do e-mail</p>", subtype="html")
print("\nEmailMessage é um builder: cabeçalhos, conteúdo e alternativas, passo a passo ->", [p.get_content_type() for p in msg.walk()])
parts = []
for i in range(3):
    parts.append(f"linha {i}")
print("lista + ''.join é o builder de strings:", " | ".join(parts), "(e é o jeito de montar textos grandes sem copiar a cada passo)")


# --- 6. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nPizza (dataclass):", measure([Pizza]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


print(f"montar uma pizza com o construtor: {best(lambda: Pizza(size='large', toppings=('queijo', 'cogumelo'), extra_sauce=True)):5.0f} ns")
print(f"montar uma consulta com o builder imutável (3 passos): {best(lambda: Query('users').select('id').where('age', '>', 1).limit(5).build()):5.0f} ns")


@dataclass(kw_only=True)
class PizzaMutable:
    size: str
    dough: str = "tradicional"
    toppings: tuple = ()
    extra_sauce: bool = False


print(f"mesma pizza com um dataclass NÃO congelado: {best(lambda: PizzaMutable(size='large', toppings=('queijo', 'cogumelo'), extra_sauce=True)):5.0f} ns (o frozen=True custa o __setattr__ de cada campo)")
print("o custo do builder imutável vem do dataclasses.replace (uma reconstrução por passo); para 3 passos a consulta leva microssegundos: irrelevante ao lado de uma ida ao banco")
