"""Gabarito do exercício 2."""
from dataclasses import dataclass, replace

COUPONS = {"DEZ": 10, "CINCO": 5}


def money(cents):
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


def _index(cart, name):
    for i, item in enumerate(cart.items):
        if item.name == name:
            return i
    raise ValueError(f"item inexistente: {name}")


def update(cart, msg):
    match msg:
        case AddItem(name, price):
            for i, item in enumerate(cart.items):
                if item.name == name:
                    return replace(cart, items=cart.items[:i] + (replace(item, qty=item.qty + 1),) + cart.items[i + 1:])
            return replace(cart, items=cart.items + (Item(name, price),))
        case RemoveItem(name):
            i = _index(cart, name)
            return replace(cart, items=cart.items[:i] + cart.items[i + 1:])
        case SetQty(name, qty):
            if qty < 0:
                raise ValueError("quantidade inválida")
            i = _index(cart, name)
            if qty == 0:
                return replace(cart, items=cart.items[:i] + cart.items[i + 1:])
            return replace(cart, items=cart.items[:i] + (replace(cart.items[i], qty=qty),) + cart.items[i + 1:])
        case ApplyCoupon(code):
            if code not in COUPONS:
                raise ValueError(f"cupom inválido: {code}")
            return replace(cart, coupon=code)
        case ClearCoupon():
            return replace(cart, coupon=None)
        case _:
            raise ValueError(f"mensagem inválida: {msg!r}")


def subtotal_cents(cart):
    return sum(item.price_cents * item.qty for item in cart.items)


def discount_cents(cart):
    return 0 if cart.coupon is None else subtotal_cents(cart) * COUPONS[cart.coupon] // 100


def total_cents(cart):
    return subtotal_cents(cart) - discount_cents(cart)


def view(cart):
    if not cart.items:
        return "carrinho vazio"
    lines = [f"{item.qty}x {item.name}: {money(item.price_cents * item.qty)}" for item in cart.items]
    if cart.coupon:
        lines.append(f"cupom {cart.coupon}: -{money(discount_cents(cart))}")
    lines.append(f"total: {money(total_cents(cart))}")
    return "\n".join(lines)
