"""Null Object em Python: os "nulos" da biblioteca padrão, coleções vazias, valores padrão, funções que não fazem nada e o objeto camaleão."""
import contextlib
import io
import logging
import os
import threading
import time
from dataclasses import dataclass

# --- 1. a biblioteca padrão está cheia de Null Objects ---
lib = logging.getLogger("minhalib.sem_handler")
buffer = io.StringIO()
with contextlib.redirect_stderr(buffer):
    lib.warning("aviso 1")
print("logger sem handler, aviso 1 foi para o stderr (o 'último recurso'):", repr(buffer.getvalue()))
lib.addHandler(logging.NullHandler())                       # o padrão de TODA biblioteca: quem usa decide como registrar
buffer = io.StringIO()
with contextlib.redirect_stderr(buffer):
    lib.warning("aviso 2")
print("com logging.NullHandler:", repr(buffer.getvalue()), "(nada saiu: a biblioteca não impõe saída a quem a usa)")

with open(os.devnull, "w") as sink:                         # um arquivo que descarta tudo
    sink.write("isto some")
print("os.devnull (um arquivo que aceita a escrita e a descarta): escreveu sem erro e sem deixar rastro")

lock = threading.Lock()


def work(lock=None):
    with (lock if lock is not None else contextlib.nullcontext()):         # um gerenciador de contexto que não faz nada
        return "feito"


print("contextlib.nullcontext: com trava ->", work(lock), "| sem trava ->", work())

# --- 2. a coleção vazia é o Null Object mais comum ---
ORDERS = {1: [{"total": 30}, {"total": 70}]}


def find_orders(user_id):
    return ORDERS.get(user_id, ())                          # o usuário 2 existe? não: devolve (), e não None


for uid in (1, 2):
    print(f"usuário {uid}: {len(find_orders(uid))} pedidos, soma {sum(o['total'] for o in find_orders(uid))} | sem nenhum 'if orders is not None'")

# --- 3. os valores padrão da própria linguagem ---
config = {"timeout": 0, "name": ""}
print("\nconfig.get('timeout') or 30 ->", config.get("timeout") or 30, "(BUG: o 0 é válido e foi trocado)", "| config.get('timeout', 30) ->", config.get("timeout", 30))
print("next(iter([]), None) ->", next(iter([]), None), "| getattr(obj, 'x', 'padrão') ->", getattr(object(), "x", "padrão"), "| o padrão vai no argumento, não em um 'if'")


# --- 4. a função que não faz nada ---
def noop(*args, **kwargs):
    return None


def process(items, on_progress=noop):
    for i, _ in enumerate(items, 1):
        on_progress(i, len(items))                          # sem 'if on_progress:'
    return len(items)


seen = []
process("abc")
process("abc", lambda i, n: seen.append(f"{i}/{n}"))
print("\non_progress padrão (noop): rodou sem callback | com callback:", seen)
identity = lambda value: value                              # o "Null Object" de uma transformação
print("transformação padrão (identidade):", [identity(x) for x in (1, 2, 3)], "| default de um parâmetro 'normalize=identity'")


# --- 5. a instância do caso especial ---
@dataclass(frozen=True)
class User:
    name: str
    discount_pct: int = 0
    is_guest: bool = False


GUEST = User("visitante", 0, is_guest=True)
USERS = {1: User("Ana", 10)}


def find_user(user_id):
    return USERS.get(user_id, GUEST)


def total(user_id, cents):
    user = find_user(user_id)
    return cents * (100 - user.discount_pct) // 100


print("\ncaso especial (um User comum, imutável, com valores neutros):", find_user(2), "| total(2, 1000) =", total(2, 1000), "| GUEST é um valor, não uma classe a mais")


# --- 6. o camaleão: um objeto que responde a TUDO ---
class Null:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)                      # os métodos "mágicos" que o Python procura não podem virar Null
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __getitem__(self, key):
        return self

    def __bool__(self):
        return False

    def __iter__(self):
        return iter(())

    def __repr__(self):
        return "Null"


NULL = Null()
print("\ncamaleão: NULL.db.host.upper() ->", NULL.db.host.upper(), "| NULL['a']['b'] ->", NULL["a"]["b"], "| bool ->", bool(NULL), "| list(NULL) ->", list(NULL))
print("O PERIGO: NULL.nmae (erro de digitação) ->", NULL.nmae, "(passa em silêncio, o bug fica escondido)")

# --- 7. a alternativa: tornar a ausência EXPLÍCITA no tipo ---
def find_or_none(user_id) -> User | None:
    return USERS.get(user_id)


def describe(user_id):
    match find_or_none(user_id):
        case None:
            return "sem usuário"                            # o verificador de tipos OBRIGA a tratar este caso
        case User(name, discount_pct):
            return f"{name} ({discount_pct}%)"


print("\nUser | None + match:", describe(1), "|", describe(2), "(a ausência é visível na assinatura; nada é escondido)")


# --- 8. o custo ---
def best(fn, n=1_000_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


class Plain:
    attr = 1


plain = Plain()
no_callback, with_noop = None, noop


def guard_callback():
    if no_callback is not None:
        no_callback(1, 2)


print(f"\nchamar um callback ausente: guarda 'if cb is not None' {best(guard_callback):3.0f} ns | noop {best(lambda: with_noop(1, 2)):3.0f} ns")
print(f"acessar um atributo: objeto comum {best(lambda: plain.attr):3.0f} ns | camaleão (via __getattr__) {best(lambda: NULL.attr):3.0f} ns")
