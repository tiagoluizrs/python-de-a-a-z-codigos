"""O: Aberto/Fechado. Aberto para EXTENSÃO, fechado para MODIFICAÇÃO. Acrescentar um caso não deve editar o código que já funciona."""
import difflib
import time
from dataclasses import dataclass
from functools import singledispatch
from typing import Protocol

# --- 1. a versão que viola: cada novo tipo de cliente EDITA a função (e o teste dela) ---
V1 = '''
def discount(customer_type, total):
    if customer_type == "regular":
        return 0.0
    elif customer_type == "vip":
        return total * 0.10
    elif customer_type == "employee":
        return total * 0.20
    else:
        raise ValueError(customer_type)
'''
V2 = V1.replace('''    else:
        raise ValueError(customer_type)''', '''    elif customer_type == "partner":
        return total * 0.15
    else:
        raise ValueError(customer_type)''')


def changed_lines(before: str, after: str) -> tuple[int, int]:
    diff = list(difflib.unified_diff(before.strip().splitlines(), after.strip().splitlines(), lineterm="", n=0))
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    return added, removed


a, r = changed_lines(V1, V2)
print(f"if/elif: acrescentar 'partner' = +{a} linhas, -{r} linhas NO CÓDIGO QUE JÁ FUNCIONAVA (e a função inteira precisa ser retestada)")

# --- 2. a versão aberta: um registro (strategy + registry); o caso novo é um módulo NOVO ---
DISCOUNTS: dict[str, "DiscountRule"] = {}


class DiscountRule(Protocol):
    def apply(self, total: float) -> float: ...


def discount_rule(name: str):
    """Decorador de registro: quem escreve uma regra nova só a MARCA; nenhuma linha existente muda."""
    def register(cls):
        DISCOUNTS[name] = cls()
        return cls
    return register


@discount_rule("regular")
class Regular:
    def apply(self, total):
        return 0.0


@discount_rule("vip")
class Vip:
    def apply(self, total):
        return total * 0.10


@discount_rule("employee")
class Employee:
    def apply(self, total):
        return total * 0.20


def discount_open(customer_type: str, total: float) -> float:
    try:
        return DISCOUNTS[customer_type].apply(total)           # esta função NUNCA mais muda
    except KeyError:
        raise ValueError(customer_type) from None


print("registro:", {k: discount_open(k, 200.0) for k in DISCOUNTS})


# o caso novo, em OUTRO arquivo (aqui, só mais abaixo): nada acima foi editado
@discount_rule("partner")
class Partner:
    def apply(self, total):
        return total * 0.15


print("depois de registrar 'partner' (código novo, sem editar o antigo):", discount_open("partner", 200.0))
print("`discount_open` ficou IGUAL: fechada para modificação; o conjunto de regras ficou ABERTO para extensão")

# --- 3. outras formas Pythônicas de abrir: singledispatch (por TIPO), dicionário de funções, entry points ---
@dataclass
class Circle:
    r: float


@dataclass
class Rect:
    w: float
    h: float


@singledispatch
def area(shape) -> float:
    raise NotImplementedError(type(shape).__name__)


@area.register
def _(shape: Circle) -> float:
    return 3.141592653589793 * shape.r**2


@area.register
def _(shape: Rect) -> float:
    return shape.w * shape.h


@dataclass
class Triangle:
    b: float
    h: float


@area.register
def _(shape: Triangle) -> float:                           # um tipo NOVO, uma função NOVA; `area` não é editada
    return shape.b * shape.h / 2


print("\nsingledispatch:", round(area(Circle(1)), 2), area(Rect(2, 3)), area(Triangle(4, 5)), "(Triangle foi acrescentado depois, sem tocar em area)")

# --- 4. o custo em tempo: if/elif x dicionário x objeto ---
def discount_if(customer_type, total):
    if customer_type == "regular":
        return 0.0
    elif customer_type == "vip":
        return total * 0.10
    elif customer_type == "employee":
        return total * 0.20
    raise ValueError(customer_type)


discount_dict = {"regular": lambda t: 0.0, "vip": lambda t: t * 0.10, "employee": lambda t: t * 0.20}


def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


for label, fn in [("if/elif (último ramo)", lambda: discount_if("employee", 100.0)), ("dict de funções", lambda: discount_dict["employee"](100.0)),
                  ("registro de objetos (Protocol)", lambda: discount_open("employee", 100.0))]:
    print(f"  {label:<34} {best(fn):6.0f} ns")
print("a diferença entre as formas é de dezenas de nanossegundos: o argumento a favor do OCP é MANUTENÇÃO, não velocidade")

# --- 5. quando NÃO abrir: dois casos fixos e estáveis ---
print("\nquando NÃO aplicar: um `if` com 2 casos que não vão crescer (ex.: modo leitura/escrita) é MAIS claro que um registro")
print("regra de bolso (a 'regra de três'): abra a extensão quando o TERCEIRO caso aparecer, não antes")
