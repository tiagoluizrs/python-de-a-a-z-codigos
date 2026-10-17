"""Exercício 2: o estilo "Elm": ``update`` e ``view`` são funções PURAS sobre dados imutáveis (um carrinho de compras)."""
from dataclasses import dataclass, replace

COUPONS = {"DEZ": 10, "CINCO": 5}                               # código -> percentual de desconto


def money(cents: int) -> str:
    """(Pronto, NÃO edite.) ``1234`` -> ``"R$ 12,34"``."""
    return f"R$ {cents // 100},{cents % 100:02d}"


@dataclass(frozen=True)
class Item:
    name: str
    price_cents: int
    qty: int = 1


@dataclass(frozen=True)
class Cart:
    items: tuple = ()
    coupon: str | None = None


@dataclass(frozen=True)
class AddItem:
    name: str
    price_cents: int


@dataclass(frozen=True)
class RemoveItem:
    name: str


@dataclass(frozen=True)
class SetQty:
    name: str
    qty: int


@dataclass(frozen=True)
class ApplyCoupon:
    code: str


@dataclass(frozen=True)
class ClearCoupon:
    pass


def update(cart: Cart, msg) -> Cart:
    """Devolve um carrinho NOVO (o antigo nunca muda), usando ``match``:

    * ``AddItem``: item que já existe (mesmo nome): ``qty + 1`` (o preço antigo permanece); senão acrescenta ``Item(name, price_cents)`` no FIM;
    * ``RemoveItem``: tira o item; nome inexistente: ``ValueError(f"item inexistente: {nome}")``;
    * ``SetQty``: ``qty < 0``: ``ValueError("quantidade inválida")``; ``0`` remove o item; senão troca a quantidade; nome inexistente: ``ValueError(f"item inexistente: {nome}")``
      (a quantidade é conferida ANTES de procurar o item);
    * ``ApplyCoupon``: o código precisa estar em ``COUPONS`` (``ValueError(f"cupom inválido: {code}")``); substitui um cupom anterior;
    * ``ClearCoupon``: tira o cupom (sem cupom, devolve um carrinho igual);
    * qualquer outra mensagem: ``ValueError(f"mensagem inválida: {msg!r}")``."""
    raise NotImplementedError


def subtotal_cents(cart: Cart) -> int:
    """A soma de ``price_cents * qty`` de todos os itens."""
    raise NotImplementedError


def discount_cents(cart: Cart) -> int:
    """``subtotal * percentual // 100`` (aritmética de INTEIROS, sem ``float``); ``0`` sem cupom."""
    raise NotImplementedError


def total_cents(cart: Cart) -> int:
    """``subtotal - desconto``."""
    raise NotImplementedError


def view(cart: Cart) -> str:
    """O texto do carrinho: ``"carrinho vazio"`` se não há itens; senão uma linha por item, ``f"{qty}x {name}: {money(price_cents * qty)}"``, depois (só com cupom)
    ``f"cupom {code}: -{money(desconto)}"`` e, por fim, ``f"total: {money(total)}"``, tudo separado por ``"\\n"``."""
    raise NotImplementedError
