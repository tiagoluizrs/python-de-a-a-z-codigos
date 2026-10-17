"""__init_subclass__: reagir à criação de subclasses, sem metaclasse."""


class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, *, key=None, **kwargs):
        super().__init_subclass__(**kwargs)           # coopera com outras bases
        cls.key = key or cls.__name__.lower()
        if cls.key in Plugin.registry:
            raise ValueError(f"chave repetida: {cls.key}")
        Plugin.registry[cls.key] = cls


class Csv(Plugin):
    pass


class Json(Plugin, key="js"):
    pass


print(Plugin.registry)
try:
    class Csv2(Plugin, key="csv"):
        pass
except ValueError as error:
    print("ValueError:", error)


# Verificar contrato na criação da classe (erro cedo, na definição)
class Shape:
    required = ("area",)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name in cls.required:
            if not callable(getattr(cls, name, None)):
                raise TypeError(f"{cls.__name__} precisa definir {name}()")


class Square(Shape):
    def area(self):
        return 4


try:
    class Broken(Shape):
        pass
except TypeError as error:
    print("TypeError:", error)


# __set_name__: o atributo descobre seu nome (Capítulo 14)
class Field:
    def __set_name__(self, owner, name):
        print(f"  __set_name__: {owner.__name__}.{name}")
        self.name = name


class Model:
    a = Field()
    b = Field()


# Ordem: __set_name__ roda ANTES de __init_subclass__
class Tracker:
    def __init_subclass__(cls, **kw):
        print("  __init_subclass__ de", cls.__name__)


class Sub(Tracker):
    f = Field()
