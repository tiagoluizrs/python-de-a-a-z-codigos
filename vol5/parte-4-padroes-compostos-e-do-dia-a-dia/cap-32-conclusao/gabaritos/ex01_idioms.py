"""Gabarito do exercício 1 (as classes clássicas ficam no arquivo do exercício; aqui só as versões pythônicas, mais as classes que os testes usam para comparar)."""
import functools
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---- as implementações clássicas (idênticas às do exercício) ----
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total_cents): ...


class NoDiscount(DiscountStrategy):
    def apply(self, total_cents):
        return total_cents


class PercentDiscount(DiscountStrategy):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, total_cents):
        return total_cents * (100 - self.percent) // 100


class FixedDiscount(DiscountStrategy):
    def __init__(self, cents):
        self.cents = cents

    def apply(self, total_cents):
        return max(total_cents - self.cents, 0)


class Checkout:
    def __init__(self, strategy=None):
        self.strategy = strategy or NoDiscount()

    def total(self, subtotal_cents):
        return self.strategy.apply(subtotal_cents)


class ClassicConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.values = {"env": "dev", "debug": False}
        return cls._instance


class Command(ABC):
    @abstractmethod
    def execute(self): ...

    @abstractmethod
    def undo(self): ...


class AppendCommand(Command):
    def __init__(self, items, item):
        self.items, self.item = items, item

    def execute(self):
        self.items.append(self.item)

    def undo(self):
        self.items.pop()


class RemoveFirstCommand(Command):
    def __init__(self, items):
        self.items, self.removed = items, None

    def execute(self):
        self.removed = self.items.pop(0)

    def undo(self):
        self.items.insert(0, self.removed)


class ClassicHistory:
    def __init__(self):
        self._done = []

    def run(self, command):
        command.execute()
        self._done.append(command)

    def undo(self):
        if not self._done:
            raise LookupError("nada para desfazer")
        self._done.pop().undo()


class ClassicCountdown:
    def __init__(self, n):
        if n < 0:
            raise ValueError("n negativo")
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n == 0:
            raise StopIteration
        value = self.n
        self.n -= 1
        return value


class ClassicPairs:
    def __init__(self, seq):
        self.seq, self.i = seq, 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i + 1 >= len(self.seq):
            raise StopIteration
        pair = (self.seq[self.i], self.seq[self.i + 1])
        self.i += 1
        return pair


class ClassicReport(ABC):
    def render(self, rows):
        parts = [self.header(rows)]
        parts.extend(self.line(row) for row in rows)
        parts.append(self.footer(rows))
        return "\n".join(parts)

    @abstractmethod
    def header(self, rows): ...

    @abstractmethod
    def line(self, row): ...

    @abstractmethod
    def footer(self, rows): ...


class TextReport(ClassicReport):
    def header(self, rows):
        return f"RELATÓRIO ({len(rows)} linhas)"

    def line(self, row):
        return f"- {row}"

    def footer(self, rows):
        return "fim"


class HtmlReport(ClassicReport):
    def header(self, rows):
        return "<ul>"

    def line(self, row):
        return f"<li>{row}</li>"

    def footer(self, rows):
        return "</ul>"


@dataclass(frozen=True)
class Circle:
    radius: float


@dataclass(frozen=True)
class Square:
    side: float


@dataclass(frozen=True)
class Rect:
    width: float
    height: float


class ShapeFactory:
    @staticmethod
    def create(kind, *args):
        if kind == "circle":
            return Circle(*args)
        elif kind == "square":
            return Square(*args)
        elif kind == "rect":
            return Rect(*args)
        raise ValueError(f"forma desconhecida: {kind}")


# ---- as versões pythônicas ----
def no_discount(total_cents):
    return total_cents


def percent(p):
    return lambda total_cents: total_cents * (100 - p) // 100


def fixed(cents):
    return lambda total_cents: max(total_cents - cents, 0)


def checkout_total(subtotal_cents, strategy=no_discount):
    return strategy(subtotal_cents)


@functools.cache
def get_config():
    return {"env": "dev", "debug": False}


def append_cmd(items, item):
    return lambda: items.append(item), lambda: items.pop()


def remove_first_cmd(items):
    removed = []
    return lambda: removed.append(items.pop(0)), lambda: items.insert(0, removed.pop())


def run(history, pair):
    pair[0]()
    history.append(pair)


def undo(history):
    if not history:
        raise LookupError("nada para desfazer")
    history.pop()[1]()


def countdown(n):
    if n < 0:
        raise ValueError("n negativo")
    return iter(range(n, 0, -1))


def pairs(iterable):
    return itertools.pairwise(iterable)                       # a biblioteca padrão já tem o gerador de pares consecutivos


def render_report(rows, *, header, line, footer):
    return "\n".join([header(rows), *map(line, rows), footer(rows)])


TEXT = {"header": lambda rows: f"RELATÓRIO ({len(rows)} linhas)", "line": lambda row: f"- {row}", "footer": lambda rows: "fim"}
HTML = {"header": lambda rows: "<ul>", "line": lambda row: f"<li>{row}</li>", "footer": lambda rows: "</ul>"}

SHAPES = {"circle": Circle, "square": Square, "rect": Rect}


def create(kind, *args):
    if kind not in SHAPES:
        raise ValueError(f"forma desconhecida: {kind!r}; disponíveis: {', '.join(sorted(SHAPES))}")
    return SHAPES[kind](*args)
