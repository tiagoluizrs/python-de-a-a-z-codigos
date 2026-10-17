"""Exercício 1: reescrever seis implementações clássicas na forma pythônica: o MESMO comportamento, com uma fração do código."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


# =====================================================================================================================
# (Pronto, NÃO edite.) As seis implementações clássicas: os testes comparam o comportamento da sua versão com o delas.
# =====================================================================================================================
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


# =====================================================================================================================
# Suas versões. Cada uma tem um LIMITE de tamanho (linhas de código normalizadas por ``ast.unparse``, sem docstring) conferido pelos testes.
# =====================================================================================================================

# 1. Strategy -> funções. ``no_discount(total)``, ``percent(p)`` e ``fixed(cents)`` (as duas últimas DEVOLVEM uma função de ``total``) e ``checkout_total(subtotal, strategy=no_discount)``.
#    Mesmos resultados de ``Checkout``/``PercentDiscount``/``FixedDiscount``. Limite: 10 linhas no total.
def no_discount(total_cents):
    raise NotImplementedError


def percent(p):
    raise NotImplementedError


def fixed(cents):
    raise NotImplementedError


def checkout_total(subtotal_cents, strategy=no_discount):
    raise NotImplementedError


# 2. Singleton -> ``get_config()`` com ``functools.cache``: devolve SEMPRE o mesmo dicionário ``{"env": "dev", "debug": False}`` (criado na primeira chamada) e tem ``cache_clear()``. Limite: 4 linhas.
def get_config():
    raise NotImplementedError


# 3. Command com desfazer -> pares ``(do, undo)``. ``append_cmd(items, item)`` e ``remove_first_cmd(items)`` devolvem um par de funções SEM argumentos (como as classes: ``do`` de
#    ``remove_first_cmd`` numa lista vazia levanta ``IndexError`` e guarda o removido; ``undo`` o recoloca no INÍCIO); ``run(history, pair)`` executa o ``do`` e SÓ DEPOIS guarda o par na lista
#    ``history`` (se o ``do`` falha, nada é guardado); ``undo(history)`` desfaz o último (``LookupError("nada para desfazer")`` se não há). Limite: 16 linhas no total.
def append_cmd(items, item):
    raise NotImplementedError


def remove_first_cmd(items):
    raise NotImplementedError


def run(history, pair):
    raise NotImplementedError


def undo(history):
    raise NotImplementedError


# 4. Iterator -> geradores. ``countdown(n)``: o mesmo que ``ClassicCountdown`` (n, n-1, ..., 1) e, como a classe, ``ValueError("n negativo")`` NA CHAMADA (antes de iterar!, o que um gerador
#    comum NÃO faz: valide e devolva o gerador); ``iter(c) is c`` e preguiçoso (``next(countdown(10**9))`` é instantâneo). ``pairs(iterable)``: os pares consecutivos de QUALQUER iterável
#    (não só sequências; dica: a biblioteca padrão tem uma função para isso, em ``itertools``). Limite: ``countdown`` com seu auxiliar, 6 linhas; ``pairs``, 5 linhas.
def countdown(n):
    raise NotImplementedError


def pairs(iterable):
    raise NotImplementedError


# 5. Template Method -> função que recebe os passos. ``render_report(rows, *, header, line, footer)`` junta com ``"\n"``: ``header(rows)``, ``line(row)`` de cada linha e ``footer(rows)``.
#    ``TEXT`` e ``HTML`` são dicionários com as chaves ``header``, ``line`` e ``footer`` tais que ``render_report(rows, **TEXT) == TextReport().render(rows)`` (e o mesmo para HTML).
#    Limite: ``render_report``, 3 linhas.
def render_report(rows, *, header, line, footer):
    raise NotImplementedError


TEXT = {}
HTML = {}


# 6. Factory -> dicionário. ``SHAPES`` mapeia ``"circle"``, ``"square"`` e ``"rect"`` às classes; ``create(kind, *args)`` consulta o dicionário (de modo que um tipo NOVO entra com
#    ``SHAPES["triangle"] = ...``, sem editar ``create``). Tipo desconhecido: ``ValueError(f"forma desconhecida: {kind!r}; disponíveis: circle, rect, square")`` (as opções em ordem
#    alfabética, calculadas do dicionário no momento do erro). Limite: ``create``, 5 linhas.
SHAPES = {}


def create(kind, *args):
    raise NotImplementedError
