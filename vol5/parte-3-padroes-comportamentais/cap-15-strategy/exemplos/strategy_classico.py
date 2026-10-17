"""Strategy, forma clássica (GoF): uma família de algoritmos intercambiáveis, cada um em uma classe, escolhidos por quem usa."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. o problema: a política de espera entre tentativas, escolhida com if/elif dentro do código que repete ---
def retry_naive(action, attempts, policy, sleep, base=1.0):
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except ConnectionError:
            if attempt == attempts:
                raise
            if policy == "fixed":
                sleep(base)
            elif policy == "linear":
                sleep(base * attempt)
            elif policy == "exponential":
                sleep(base * 2 ** (attempt - 1))
            else:
                raise ValueError(policy)                      # uma política nova EDITA esta função


# --- 2. a forma clássica: a interface, uma classe por algoritmo, e o contexto que recebe a estratégia ---
class BackoffStrategy(ABC):
    @abstractmethod
    def delay(self, attempt: int) -> float: ...


class Fixed(BackoffStrategy):
    def __init__(self, seconds):
        self.seconds = seconds

    def delay(self, attempt):
        return self.seconds


class Linear(BackoffStrategy):
    def __init__(self, step):
        self.step = step

    def delay(self, attempt):
        return self.step * attempt


class Exponential(BackoffStrategy):
    def __init__(self, base=1.0, factor=2.0, cap=None):
        self.base, self.factor, self.cap = base, factor, cap

    def delay(self, attempt):
        value = self.base * self.factor ** (attempt - 1)
        return value if self.cap is None else min(value, self.cap)


class Retrier:                                                # o CONTEXTO
    def __init__(self, strategy: BackoffStrategy, attempts, sleep):
        self.strategy, self.attempts, self.sleep = strategy, attempts, sleep

    def run(self, action):
        for attempt in range(1, self.attempts + 1):
            try:
                return action()
            except ConnectionError:
                if attempt == self.attempts:
                    raise
                self.sleep(self.strategy.delay(attempt))


def flaky_factory(failures):
    state = {"n": 0}

    def action():
        state["n"] += 1
        if state["n"] <= failures:
            raise ConnectionError("caiu")
        return "ok"

    return action


for name, strategy in [("Fixed(2)", Fixed(2)), ("Linear(1)", Linear(1)), ("Exponential(1, cap=5)", Exponential(1, 2, cap=5))]:
    waits = []
    result = Retrier(strategy, 6, waits.append).run(flaky_factory(5))
    print(f"{name:<24} esperas entre as tentativas: {waits} -> {result}")

waits = []
retry_naive(flaky_factory(3), 5, "exponential", waits.append)
print("\nversão com if/elif (sem o padrão):", waits, "| política nova = editar a função")

# --- 3. trocar a estratégia em tempo de execução, sem tocar no contexto ---
retrier = Retrier(Fixed(1), 4, waits.append)
waits.clear()
retrier.run(flaky_factory(2))
retrier.strategy = Exponential(0.5)
retrier.run(flaky_factory(2))
print("estratégia trocada no meio:", waits)

# --- 4. o custo: contar a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nBackoffStrategy + 3 estratégias + Retrier:", measure([BackoffStrategy, Fixed, Linear, Exponential, Retrier]))


def best(fn, n=500_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


exp = Exponential(1, 2, cap=5)
print(f"calcular uma espera: {best(lambda: exp.delay(3)):4.0f} ns (um método de objeto)")
