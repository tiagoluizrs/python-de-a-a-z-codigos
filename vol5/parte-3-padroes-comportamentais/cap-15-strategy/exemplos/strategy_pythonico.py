"""Strategy em Python: a estratégia é uma FUNÇÃO (ou qualquer callable); parâmetros entram por closure, partial ou uma classe com __call__."""
import ast
import functools
import inspect
import random
import re
import textwrap
import time
from functools import singledispatch


# --- 1. a mesma família de algoritmos, como funções que devolvem funções (closures) ---
def fixed(seconds):
    return lambda attempt: seconds


def linear(step):
    return lambda attempt: step * attempt


def exponential(base=1.0, factor=2.0, cap=None):
    def delay(attempt):
        value = base * factor ** (attempt - 1)
        return value if cap is None else min(value, cap)
    return delay


def with_jitter(strategy, rng=random.random):                  # uma estratégia que ENVOLVE outra: composição de funções
    return lambda attempt: strategy(attempt) * rng()


def retry(action, strategy, attempts, sleep):
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except ConnectionError:
            if attempt == attempts:
                raise
            sleep(strategy(attempt))


def flaky_factory(failures):
    state = {"n": 0}

    def action():
        state["n"] += 1
        if state["n"] <= failures:
            raise ConnectionError("caiu")
        return "ok"

    return action


for name, strategy in [("fixed(2)", fixed(2)), ("linear(1)", linear(1)), ("exponential(1, cap=5)", exponential(1, 2, cap=5))]:
    waits = []
    retry(flaky_factory(5), strategy, 6, waits.append)
    print(f"{name:<24} esperas: {waits}")
waits = []
retry(flaky_factory(3), with_jitter(exponential(1), rng=lambda: 0.5), 5, waits.append)
print("com jitter (rng injetado = 0.5):", waits, "| a estratégia envolvendo outra é uma linha")

# --- 2. a escolha por NOME: um dicionário no lugar do if/elif ---
POLICIES = {"fixed": fixed, "linear": linear, "exponential": exponential}


def make_policy(name, *args, **kwargs):
    try:
        return POLICIES[name](*args, **kwargs)
    except KeyError:
        raise ValueError(f"política desconhecida: {name!r}; disponíveis: {', '.join(sorted(POLICIES))}") from None


print("\npor nome:", make_policy("linear", 2)(3), "| erro útil:", end=" ")
try:
    make_policy("quadratica")
except ValueError as error:
    print(error)

# --- 3. as estratégias da biblioteca padrão: o argumento key=, o repl= do re.sub, o default= do json ---
products = [("lapis", 1.5, 4.2), ("caneta", 3.0, 4.8), ("caderno", 12.0, 4.5)]
print("\nsorted(key=...): a estratégia de ordenação é um argumento")
print("  por preço   :", [p[0] for p in sorted(products, key=lambda p: p[1])])
print("  por nota    :", [p[0] for p in sorted(products, key=lambda p: -p[2])])
print("  custo-benefício:", [p[0] for p in sorted(products, key=lambda p: p[2] / p[1], reverse=True)])
print("re.sub(repl=função):", re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "3 gatos e 10 cães"))

# --- 4. escolher a estratégia pelo TIPO do dado: singledispatch ---
@singledispatch
def describe(value):
    return f"objeto {value!r}"


@describe.register
def _(value: int):
    return f"inteiro {value}"


@describe.register
def _(value: list):
    return f"lista de {len(value)}"


print("\nsingledispatch escolhe a estratégia pelo tipo:", describe(3), "|", describe([1, 2]), "|", describe("x"))


# --- 5. quando a estratégia tem ESTADO: uma classe com __call__ (continua sendo um callable) ---
class Adaptive:
    """Dobra a espera a cada falha seguida e volta ao início quando uma tentativa dá certo."""

    def __init__(self):
        self.current = 0.5

    def __call__(self, attempt):
        value = self.current
        self.current *= 2
        return value

    def success(self):
        self.current = 0.5


adaptive = Adaptive()
waits = []
retry(flaky_factory(3), adaptive, 5, waits.append)
print("\nestratégia com estado:", waits, "| é só um callable: o contexto (retry) não mudou")

# --- 6. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("fixed + linear + exponential + retry:", measure([fixed, linear, exponential, retry]))


def best(fn, n=500_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


closure = exponential(1, 2, cap=5)
partial = functools.partial(lambda base, factor, attempt: base * factor ** (attempt - 1), 1, 2)
print("\ncalcular uma espera:")
print(f"  closure           {best(lambda: closure(3)):4.0f} ns")
print(f"  functools.partial {best(lambda: partial(3)):4.0f} ns")
tester = Adaptive()
print(f"  classe __call__   {best(lambda: tester(3)):4.0f} ns")
