"""Exercício 3: estratégias de desconto, algumas sem estado (funções) e uma COM estado (classe com ``__call__``), trocáveis em um ``Checkout``."""


def no_discount(subtotal: int, lines: list) -> int:
    """Desconto zero. (Toda estratégia recebe ``(subtotal_em_centavos, lines)`` e devolve o desconto em centavos, um inteiro.)"""
    raise NotImplementedError


def percent(p: float):
    """Devolve uma estratégia que dá ``round(subtotal * p / 100)`` de desconto. ``p`` fora de 0 a 100: ``ValueError("percentual inválido")`` (na criação)."""
    raise NotImplementedError


def bulk(min_qty: int, p: float):
    """Devolve uma estratégia que dá ``p`` por cento SÓ sobre as linhas com ``qty >= min_qty`` (cada linha é ``(sku, qty, unit_cents)``): soma
    ``qty * unit_cents`` dessas linhas, aplica ``p`` e arredonda UMA vez no fim (``round``). ``min_qty < 1`` ou ``p`` fora de 0 a 100: ``ValueError``."""
    raise NotImplementedError


class Loyalty:
    """Estratégia COM ESTADO: ``Loyalty(threshold, p)``. Cada chamada ``loyalty(subtotal, lines)`` conta UM pedido (``orders`` sobe de 1); os ``threshold`` primeiros
    pedidos não têm desconto; a partir do seguinte, cada chamada dá ``round(subtotal * p / 100)``. ``reset()`` zera ``orders``. ``threshold < 0`` ou ``p`` fora
    de 0 a 100: ``ValueError``. Atributos públicos: ``orders``, ``threshold``, ``p``."""

    def __init__(self, threshold: int, p: float):
        raise NotImplementedError

    def __call__(self, subtotal: int, lines: list) -> int:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


def best_of(*strategies):
    """Uma estratégia que chama TODAS as ``strategies`` (uma vez cada, na ordem) e devolve o MAIOR desconto. Sem estratégias: ``ValueError("nenhuma estratégia")``."""
    raise NotImplementedError


class Checkout:
    """``Checkout(strategy=no_discount)``.

    * ``total(lines)``: ``lines`` é uma lista de ``(sku, qty, unit_cents)``; ``qty <= 0`` ou ``unit_cents < 0``: ``ValueError(f"linha inválida: {linha!r}")`` (a primeira
      inválida, ANTES de chamar a estratégia); o subtotal é ``sum(qty * unit_cents)``; o desconto vem de ``strategy(subtotal, lines)`` e NUNCA passa do subtotal
      (limite com ``min``); devolve ``subtotal - desconto``;
    * ``strategy`` (propriedade com ``setter``): troca a estratégia em tempo de execução; atribuir algo que não é chamável: ``TypeError("estratégia precisa ser chamável")``;
    * ``describe()``: o nome da estratégia: ``strategy.__name__`` se existir, senão o nome da classe (``type(strategy).__name__``)."""

    def __init__(self, strategy=None):
        raise NotImplementedError

    @property
    def strategy(self):
        raise NotImplementedError

    @strategy.setter
    def strategy(self, value):
        raise NotImplementedError

    def total(self, lines: list) -> int:
        raise NotImplementedError

    def describe(self) -> str:
        raise NotImplementedError
