"""__repr__, __str__ e __format__: três vozes de um objeto."""
import datetime as dt


class Plain:
    pass


print(repr(Plain()))                        # <__main__.Plain object at 0x...>


class Money:
    def __init__(self, cents, currency="BRL"):
        self.cents, self.currency = cents, currency

    def __repr__(self):
        return f"Money({self.cents!r}, {self.currency!r})"

    def __str__(self):
        reais, cents = divmod(self.cents, 100)
        return f"R$ {reais},{cents:02d}"

    def __format__(self, spec):
        if spec == "":
            return str(self)
        if spec == "plain":
            return f"{self.cents / 100:.2f}"
        if spec == "code":
            return f"{self.currency} {self.cents / 100:.2f}"
        raise ValueError(f"formato desconhecido: {spec!r}")


price = Money(1990)
print(repr(price), "|", str(price))
print(f"{price}|{price:plain}|{price:code}|{price!r}")
print([price, Money(50)])                   # contêineres usam repr dos itens
print("print(price):", price)               # print usa str
try:
    f"{price:xyz}"
except ValueError as error:
    print("ValueError:", error)

# Sem __str__, o str() recorre ao __repr__ (o contrário NÃO vale)
class OnlyRepr:
    def __repr__(self):
        return "OnlyRepr()"


class OnlyStr:
    def __str__(self):
        return "texto"


print(str(OnlyRepr()), "|", repr(OnlyStr())[:22] + "...")

# Objetos sem __format__ próprio rejeitam especificações
plain = Plain()
try:
    format(plain, ">10")
except TypeError as error:
    print("TypeError:", error)
print(format(plain, "") == str(plain))

# Datas implementam __format__ com strftime
moment = dt.datetime(2026, 10, 12, 9, 5)
print(f"{moment:%d/%m/%Y %H:%M}", "|", moment.__format__("%A"))
