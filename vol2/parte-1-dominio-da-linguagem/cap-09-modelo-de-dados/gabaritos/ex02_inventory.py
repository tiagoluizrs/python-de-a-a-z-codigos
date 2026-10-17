"""Gabarito do exercício 2."""


class Inventory:
    def __init__(self, **stock):
        self._stock = {}
        for sku, quantity in stock.items():
            self[sku] = quantity                        # reaproveita a validação

    def __len__(self):
        return len(self._stock)

    def __getitem__(self, sku):
        return self._stock[sku]

    def __setitem__(self, sku, quantity):
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
            raise ValueError(f"quantidade inválida: {quantity!r}")
        if quantity == 0:
            self._stock.pop(sku, None)                  # zero remove
        else:
            self._stock[sku] = quantity

    def __delitem__(self, sku):
        del self._stock[sku]

    def __contains__(self, sku):
        return sku in self._stock

    def __iter__(self):
        return iter(self._stock)

    def __repr__(self):
        return f"Inventory({self._stock!r})"
