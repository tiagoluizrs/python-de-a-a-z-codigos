"""Código sob teste usado pelos exemplos do capítulo."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


def apply_discount(price, percent):
    """Preço com desconto, arredondado a 2 casas. ``percent`` entre 0 e 100."""
    if not 0 <= percent <= 100:
        raise ValueError(f"percentual inválido: {percent}")
    return round(price * (1 - percent / 100), 2)


def parse_price(text):
    """``"R$ 1.234,56"`` -> ``Decimal("1234.56")``."""
    cleaned = text.replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except ArithmeticError:
        raise ValueError(f"preço inválido: {text!r}") from None


@dataclass
class Cart:
    items: dict = field(default_factory=dict)          # sku -> (preço, quantidade)

    def add(self, sku, price, qty=1):
        if qty < 1:
            raise ValueError("quantidade deve ser >= 1")
        old_price, old_qty = self.items.get(sku, (price, 0))
        self.items[sku] = (old_price, old_qty + qty)

    def total(self):
        return sum(price * qty for price, qty in self.items.values())


def days_until(due, today=None):
    today = today or date.today()
    return (due - today).days


def fetch_rate(client, currency):
    """Busca a cotação por um cliente HTTP injetado (``client.get_json(url)``)."""
    data = client.get_json(f"https://api.example.com/rates/{currency}")
    if "rate" not in data:
        raise KeyError("resposta sem 'rate'")
    return Decimal(str(data["rate"]))
