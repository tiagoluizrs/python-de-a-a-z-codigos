"""Operadores aumentados: += usa __iadd__, e cai para __add__."""


class Basket:
    def __init__(self, *items):
        self.items = list(items)

    def __repr__(self):
        return f"Basket({self.items!r})"

    def __add__(self, other):
        print("  __add__ (cria um objeto novo)")
        return Basket(*self.items, *other.items)

    def __iadd__(self, other):
        print("  __iadd__ (altera no lugar)")
        self.items.extend(other.items)
        return self                              # OBRIGATÓRIO devolver o resultado


b1 = Basket(1)
alias = b1
b1 += Basket(2)
print(b1, "| alias vê a mudança:", alias is b1, alias)


class NoInplace:
    def __init__(self, n):
        self.n = n

    def __add__(self, other):
        return NoInplace(self.n + other.n)

    def __repr__(self):
        return f"NoInplace({self.n})"


x = NoInplace(1)
alias = x
x += NoInplace(2)                                # cai para __add__
print(x, "| alias:", alias, "| mesmo objeto?", x is alias)


class Forgetful:
    def __iadd__(self, other):
        pass                                     # esqueceu o return!


f = Forgetful()
f += 1
print("depois de f += 1, f vale:", f)
