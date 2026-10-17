"""Mixins: capacidades pequenas e combináveis."""
import json


class ReprMixin:
    """Dá um __repr__ a partir dos atributos da instância."""

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"


class JsonMixin:
    """Serializa para JSON os atributos da instância."""

    def to_json(self):
        return json.dumps(vars(self), sort_keys=True)


class OrderMixin:
    """Ordena por self.sort_key() (a classe concreta o fornece)."""

    def __lt__(self, other):
        return self.sort_key() < other.sort_key()


class Product(ReprMixin, JsonMixin, OrderMixin):
    def __init__(self, name, price):
        self.name, self.price = name, price

    def sort_key(self):
        return self.price


items = [Product("b", 9.5), Product("a", 3.0), Product("c", 7.25)]
print(sorted(items))
print(items[0].to_json())
print([c.__name__ for c in Product.__mro__])
print(isinstance(items[0], JsonMixin))

# Ordem das bases: o mixin vem ANTES da classe base, para poder sobrescrever
class Loud:
    def speak(self):
        return super().speak().upper() + "!"


class Dog:
    def speak(self):
        return "au"


class LoudDog(Loud, Dog):             # Loud primeiro: ele decora o speak de Dog
    pass


class QuietDog(Dog, Loud):            # Dog primeiro: Loud nunca é consultado
    pass


print(LoudDog().speak(), "|", QuietDog().speak())
