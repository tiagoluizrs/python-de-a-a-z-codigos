"""Um contêiner completo: len, getitem, setitem, delitem, in, iter."""


class Inventory:
    """Estoque: código do produto -> quantidade."""

    def __init__(self, **stock):
        self._stock = dict(stock)

    def __len__(self):
        return len(self._stock)

    def __getitem__(self, sku):
        return self._stock[sku]               # KeyError natural

    def __setitem__(self, sku, quantity):
        if quantity < 0:
            raise ValueError("quantidade negativa")
        self._stock[sku] = quantity

    def __delitem__(self, sku):
        del self._stock[sku]

    def __contains__(self, sku):
        return sku in self._stock

    def __iter__(self):
        return iter(self._stock)

    def __repr__(self):
        return f"Inventory({self._stock!r})"


stock = Inventory(apple=3, pear=5)
print(len(stock), "apple" in stock, "kiwi" in stock, list(stock))
stock["kiwi"] = 7
del stock["pear"]
print(stock, bool(stock), bool(Inventory()))
try:
    stock["plum"]
except KeyError as error:
    print("KeyError:", error)
for sku in stock:
    print(" ", sku, stock[sku])

# Só __getitem__ já basta para iterar, testar `in` e reversed (protocolo antigo)
class OnlyGetitem:
    def __init__(self, *items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index]


old = OnlyGetitem(10, 20, 30)
print(list(old), 20 in old, max(old))
try:
    reversed(old)
except TypeError as error:
    print("TypeError:", error)


class WithLen(OnlyGetitem):
    def __len__(self):
        return len(self.items)


print(list(reversed(WithLen(10, 20, 30))))
