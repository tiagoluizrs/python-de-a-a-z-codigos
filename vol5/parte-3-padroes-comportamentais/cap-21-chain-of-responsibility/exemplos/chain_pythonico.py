"""Chain of Responsibility em Python: uma lista de funções, o middleware (cada elo chama o próximo), ChainMap e a cadeia do logging."""
import ast
import inspect
import io
import logging
import textwrap
import time
from collections import ChainMap
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    amount: float
    description: str


# --- 1. a cadeia como LISTA: o primeiro que devolve algo (não None) resolve ---
def lead(expense):
    if expense.amount <= 1_000:
        return f"líder aprovou {expense.description}"


def manager(expense):
    if expense.amount <= 10_000:
        return f"gerente aprovou {expense.description}"


def director(expense):
    if expense.amount <= 100_000:
        return f"diretor aprovou {expense.description}"


APPROVERS = [lead, manager, director]


def first_match(handlers, request, default=None):
    return next(filter(None, (h(request) for h in handlers)), default)      # preguiçoso: para no primeiro que resolve


for amount in (300, 5_000, 50_000, 500_000):
    print(f"{amount:>9,}:", first_match(APPROVERS, Expense(amount, "pedido"), default="recusado (ninguém tem alçada)"))
print("a cadeia é UMA LISTA: reordenar, acrescentar e remover níveis é mexer na lista; o `default` trata o 'ninguém resolveu'")

# --- 2. o middleware: cada elo recebe o pedido E o próximo elo, e decide se chama (e o que faz antes e depois) ---
def logging_mw(log):
    def middleware(request, call_next):
        log.append(f"→ {request['path']}")
        response = call_next(request)
        log.append(f"← {response['status']}")
        return response
    return middleware


def auth_mw(valid_tokens):
    def middleware(request, call_next):
        if request.get("token") not in valid_tokens:
            return {"status": 401, "body": "não autorizado"}            # CURTO-CIRCUITO: o pedido não passa adiante
        return call_next(request)
    return middleware


def timing_mw(sink):
    def middleware(request, call_next):
        start = time.perf_counter()
        try:
            return call_next(request)
        finally:
            sink.append(round((time.perf_counter() - start) * 1e6))
    return middleware


def compose(*middlewares):
    """compose(a, b, c)(handler): a(b(c(handler))): o PRIMEIRO da lista é o mais EXTERNO."""
    def wrap(handler):
        for mw in reversed(middlewares):
            handler = (lambda mw_, nxt: lambda request: mw_(request, nxt))(mw, handler)
        return handler
    return wrap


def app(request):
    return {"status": 200, "body": f"olá, {request['path']}"}


log, timings = [], []
pipeline = compose(logging_mw(log), auth_mw({"segredo"}), timing_mw(timings))(app)
print("\nmiddleware com token válido:", pipeline({"path": "/home", "token": "segredo"}), "| log:", log)
log.clear()
print("sem token (o auth barra antes do app):", pipeline({"path": "/admin"}), "| log:", log, "| o timing nem rodou:", len(timings) == 1)

print("a ordem importa: com o logging DEPOIS do auth, o pedido barrado não é registrado:")
log2 = []
inner = compose(auth_mw({"x"}), logging_mw(log2))(app)
inner({"path": "/a", "token": "errado"})
print("  log vazio:", log2 == [])

# --- 3. collections.ChainMap: a cadeia de busca da biblioteca padrão (cada camada é um dicionário) ---
defaults = {"color": "azul", "size": 10, "debug": False}
file_values = {"size": 12}
env = {"debug": True}
cli = {"color": "verde"}
config = ChainMap(cli, env, file_values, defaults)                      # a PRIMEIRA camada que tiver a chave responde
print("\nChainMap (cli > env > arquivo > padrões):", dict(config), "| size vem de:", next(i for i, layer in enumerate(config.maps) if "size" in layer), "(índice 2: o arquivo)")
config["size"] = 99                                                       # escrever vai SEMPRE para a primeira camada
print("escrita vai à primeira camada:", cli, "| os padrões continuam intactos:", defaults["size"])

# --- 4. o logging é uma cadeia: o registro SOBE pela hierarquia de loggers (propagate) até um que o trate ---
stream = io.StringIO()
root_handler = logging.StreamHandler(stream)
parent = logging.getLogger("app")
parent.setLevel(logging.INFO)
parent.addHandler(root_handler)
parent.propagate = False
child = logging.getLogger("app.db.pool")                                  # sem handler próprio: o registro sobe para "app.db", "app", ...
child.info("conexão aberta")
print("\nlogging: o registro de 'app.db.pool' subiu a cadeia até o handler de 'app' ->", repr(stream.getvalue()))


# --- 5. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nlista de funções (3 aprovadores + first_match):", measure([lead, manager, director, first_match]), "(contra 24 linhas e 2 classes do clássico, sem os níveis)")


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


big = Expense(50_000, "licenças")
print(f"pedido que desce 3 níveis: lista {best(lambda: first_match(APPROVERS, big)):4.0f} ns")
bare = compose()(app)
three = compose(*[lambda r, n: n(r)] * 3)(app)
ten = compose(*[lambda r, n: n(r)] * 10)(app)
req = {"path": "/", "token": "x"}
print(f"middleware: sem camadas {best(lambda: bare(req)):4.0f} ns | 3 camadas {best(lambda: three(req)):4.0f} ns | 10 camadas {best(lambda: ten(req)):4.0f} ns (~{(best(lambda: ten(req)) - best(lambda: bare(req))) / 10:.0f} ns por camada)")
