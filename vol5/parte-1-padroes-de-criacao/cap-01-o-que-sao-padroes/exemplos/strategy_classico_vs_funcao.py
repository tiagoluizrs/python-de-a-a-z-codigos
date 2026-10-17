"""O mesmo padrão (Strategy: trocar o algoritmo sem editar quem o usa) em duas formas: a clássica, com classes, e a que o Python permite."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. a forma clássica (GoF): uma interface, uma classe por algoritmo, e um contexto que recebe a estratégia ---
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float: ...


class NoDiscount(DiscountStrategy):
    def apply(self, total):
        return total


class PercentDiscount(DiscountStrategy):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, total):
        return total * (1 - self.percent / 100)


class FixedDiscount(DiscountStrategy):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, total):
        return max(total - self.amount, 0.0)


class Checkout:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def total(self, subtotal):
        return round(self.strategy.apply(subtotal), 2)


# --- 2. a forma pythônica: a "estratégia" é uma função; quem precisa de parâmetro usa closure ou functools.partial ---
def no_discount(total):
    return total


def percent(p):
    return lambda total: total * (1 - p / 100)


def fixed(amount):
    return lambda total: max(total - amount, 0.0)


def checkout_total(subtotal, strategy=no_discount):
    return round(strategy(subtotal), 2)


classic = Checkout(PercentDiscount(10)).total(200.0)
pythonic = checkout_total(200.0, percent(10))
print(f"mesmo resultado: classico={classic} pythonico={pythonic}\n")


# --- 3. medir a cerimônia: linhas, classes e funções de cada versão ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree)),
            "funções": sum(isinstance(n, (ast.FunctionDef, ast.Lambda)) for n in ast.walk(tree))}


m_classic = measure([DiscountStrategy, NoDiscount, PercentDiscount, FixedDiscount, Checkout])
m_python = measure([no_discount, percent, fixed, checkout_total])
print("clássico :", m_classic)
print("pythônico:", m_python)

# --- 4. e o custo em tempo ---
def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


c = Checkout(PercentDiscount(10))
p = percent(10)
t_classic = best(lambda: c.total(200.0))
t_python = best(lambda: checkout_total(200.0, p))
print(f"\nclássico {t_classic:5.0f} ns | pythônico {t_python:5.0f} ns por chamada (a diferença é de dezenas de ns: o ganho é de leitura e de manutenção)")

# --- 5. quando a classe VOLTA a ser a escolha certa: a estratégia tem ESTADO, vários métodos ou precisa ser inspecionada ---
class Tiered:
    """Desconto por faixa de consumo acumulado: tem estado e mais de um método, então uma classe se paga."""

    def __init__(self):
        self.accumulated = 0.0

    def apply(self, total):
        self.accumulated += total
        return total * (0.9 if self.accumulated > 500 else 1.0)

    def reset(self):
        self.accumulated = 0.0


t = Tiered()
print("\ncom estado e dois métodos, a classe é honesta:", [round(t.apply(300.0), 2) for _ in range(3)], "(o callable ainda serve: Tiered.apply é só um método ligado)")
print("regra: comece pela função; vire classe quando aparecer estado, mais de uma operação ou a necessidade de listar/identificar as variantes")
