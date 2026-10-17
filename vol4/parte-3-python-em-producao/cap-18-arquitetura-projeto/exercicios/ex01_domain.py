"""Exercício 1: o DOMÍNIO de um carrinho de compras: regras puras, sem nenhuma dependência de infraestrutura."""
from dataclasses import dataclass, field
from decimal import Decimal


class DomainError(Exception):
    """Uma regra de negócio foi violada."""


class Money:
    """Dinheiro como VALOR (imutável, comparável, usável como chave de dict): ``Money("10.5")`` guarda ``Decimal("10.50")``.

    * o valor é arredondado a 2 casas com arredondamento meio-par (``"2.675"`` -> ``2.68``, ``"2.665"`` -> ``2.66``);
      aceita ``str``, ``int`` e ``Decimal`` (NÃO ``float``: ``TypeError``, porque o ``float`` já chegou impreciso);
    * ``+`` e ``-`` entre ``Money``; ``*`` por ``int`` ou ``Decimal`` (``Money * 3`` e ``3 * Money``); resultado sempre ``Money``;
    * ``==``, ``<``, ``<=``, ``>``, ``>=`` entre ``Money``; ``hash`` coerente com ``==``;
    * ``str(Money("1234.5"))`` é ``"R$ 1.234,50"``; ``repr`` é ``Money('1234.50')``;
    * a propriedade ``amount`` devolve o ``Decimal``."""

    def __init__(self, value):
        raise NotImplementedError


@dataclass
class Cart:
    """Carrinho: ``items`` mapeia ``sku -> (quantidade, preço unitário Money)``.

    Regras (todas violações levantam ``DomainError`` com mensagens úteis):

    * ``add(sku, qty, unit_price)``: ``qty`` inteira e positiva; soma à quantidade existente (o preço unitário passa a ser o
      mais novo); no máximo 10 unidades de CADA sku e 30 unidades no total;
    * ``remove(sku, qty=None)``: sem ``qty``, tira o sku inteiro; com ``qty``, tira essa quantidade (``qty`` maior que a
      existente: ``DomainError``; ficar com 0 remove o sku); sku inexistente: ``DomainError``;
    * ``apply_coupon(code, percent)``: ``percent`` é ``Decimal`` entre ``0`` (exclusive) e ``0.30`` (inclusive); só UM cupom por
      carrinho (outro: ``DomainError``);
    * ``subtotal()``: soma de ``qty * preço``; ``total()``: ``subtotal`` menos o desconto do cupom (``Money``);
    * ``checkout()``: carrinho vazio -> ``DomainError``; total abaixo de ``Money("10.00")`` -> ``DomainError``; funciona uma vez:
      muda ``status`` de ``"open"`` para ``"closed"``; depois de fechado, ``add``, ``remove``, ``apply_coupon`` e ``checkout``
      levantam ``DomainError``."""

    items: dict = field(default_factory=dict)
    coupon: tuple | None = None
    status: str = "open"

    def add(self, sku: str, qty: int, unit_price: Money) -> None:
        raise NotImplementedError

    def remove(self, sku: str, qty: int | None = None) -> None:
        raise NotImplementedError

    def apply_coupon(self, code: str, percent: Decimal) -> None:
        raise NotImplementedError

    def subtotal(self) -> Money:
        raise NotImplementedError

    def total(self) -> Money:
        raise NotImplementedError

    def checkout(self) -> None:
        raise NotImplementedError
