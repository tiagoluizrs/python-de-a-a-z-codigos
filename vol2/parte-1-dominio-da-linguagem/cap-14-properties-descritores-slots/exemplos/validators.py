"""Descritores reutilizáveis: validação declarada uma vez, usada em vários atributos."""


class Validator:
    def __set_name__(self, owner, name):
        self.private_name = "_" + name              # onde o valor mora, em cada instância
        self.public_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                              # Classe.attr devolve o descritor
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    def validate(self, value):
        raise NotImplementedError


class Positive(Validator):
    def validate(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{self.public_name} deve ser positivo, recebi {value!r}")


class NonEmpty(Validator):
    def validate(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{self.public_name} não pode ser vazio")


class OneOf(Validator):
    def __init__(self, *choices):
        self.choices = choices

    def validate(self, value):
        if value not in self.choices:
            raise ValueError(f"{self.public_name} deve ser um de {self.choices}, recebi {value!r}")


class Product:
    name = NonEmpty()
    price = Positive()
    unit = OneOf("kg", "un", "l")

    def __init__(self, name, price, unit):
        self.name, self.price, self.unit = name, price, unit


apple = Product("maçã", 4.5, "kg")
print(apple.name, apple.price, apple.unit, vars(apple))
for kwargs in ({"name": " ", "price": 1, "unit": "kg"},
               {"name": "x", "price": -1, "unit": "kg"},
               {"name": "x", "price": 1, "unit": "m"}):
    try:
        Product(**kwargs)
    except ValueError as error:
        print("ValueError:", error)

pear = Product("pera", 3, "un")
print(apple.price, pear.price, Product.price.__class__.__name__)    # estado por instância


# A ARMADILHA: guardar o valor no próprio descritor compartilha entre instâncias
class BadPositive:
    def __init__(self):
        self.value = None

    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        self.value = value                           # um só valor para TODAS as instâncias


class Shared:
    amount = BadPositive()


a, b = Shared(), Shared()
a.amount = 1
b.amount = 2
print("a.amount =", a.amount, "(esperado 1)")
