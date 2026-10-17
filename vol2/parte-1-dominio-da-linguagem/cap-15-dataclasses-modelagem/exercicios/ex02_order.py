"""Exercício 2: um agregado imutável (value objects)."""
from decimal import Decimal


class LineItem:
    """``@dataclass(frozen=True)`` com ``sku: str``, ``quantity: int`` (> 0) e
    ``unit_price: Decimal``; propriedade ``total`` = quantity * unit_price."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Order:
    """``@dataclass(frozen=True)`` com ``customer: str`` e ``items: tuple``
    (padrão ``()``), de ``LineItem``.

    * propriedade ``total``: soma dos totais dos itens (``Decimal("0")`` se
      vazio);
    * ``add(item)`` devolve um NOVO ``Order`` com o item acrescentado (use
      ``dataclasses.replace``); o original NÃO muda;
    * ``hash(order)`` funciona (é imutável).
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
