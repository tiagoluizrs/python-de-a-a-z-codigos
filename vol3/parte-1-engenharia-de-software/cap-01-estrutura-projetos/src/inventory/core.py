"""Regras de negócio: nada de arquivos, nada de print."""
from dataclasses import dataclass, replace

from ._util import normalize_sku


class OutOfStockError(Exception):
    """Tentativa de retirar mais do que existe."""


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    qty: int = 0

    def __post_init__(self):
        if self.qty < 0:
            raise ValueError("quantidade não pode ser negativa")
        object.__setattr__(self, "sku", normalize_sku(self.sku))


class Inventory:
    def __init__(self, items=()):
        self._items = {}
        for item in items:
            self.add(item)

    def add(self, item):
        current = self._items.get(item.sku)
        if current is None:
            self._items[item.sku] = item
        else:
            self._items[item.sku] = replace(current, qty=current.qty + item.qty)

    def remove(self, sku, qty):
        sku = normalize_sku(sku)
        current = self._items.get(sku)
        if current is None or current.qty < qty:
            raise OutOfStockError(f"estoque insuficiente de {sku}")
        self._items[sku] = replace(current, qty=current.qty - qty)

    def items(self):
        return sorted(self._items.values(), key=lambda item: item.sku)

    def total_quantity(self):
        return sum(item.qty for item in self._items.values())
