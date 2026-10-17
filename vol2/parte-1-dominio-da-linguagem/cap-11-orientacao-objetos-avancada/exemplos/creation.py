"""Criação de instância: __new__ constrói, __init__ inicializa."""


class Traced:
    def __new__(cls, *args, **kwargs):
        print(f"  __new__({cls.__name__}, {args})")
        instance = super().__new__(cls)
        return instance                       # o que __new__ devolve vira o resultado

    def __init__(self, value):
        print(f"  __init__({value})")
        self.value = value


print("Traced(1):")
t = Traced(1)


# Se __new__ NÃO devolve uma instância da classe, o __init__ não roda
class Weird:
    def __new__(cls, *args):
        return "outra coisa"

    def __init__(self, *args):
        print("  __init__ (não aparece)")


print("Weird():", Weird())


# Flyweight/cache: __new__ pode devolver uma instância existente
class Currency:
    _cache = {}

    def __new__(cls, code):
        if code not in cls._cache:
            instance = super().__new__(cls)
            instance.code = code
            cls._cache[code] = instance
        return cls._cache[code]


print(Currency("BRL") is Currency("BRL"), Currency("USD") is Currency("BRL"))


# Singleton: __init__ roda a CADA chamada (pegadinha)
class Singleton:
    _instance = None
    calls = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        Singleton.calls += 1


first, second = Singleton(), Singleton()
print("mesma instância:", first is second, "| __init__ rodou", Singleton.calls, "vezes")


# Tipos imutáveis exigem __new__ (o valor é fixado na construção)
class Celsius(float):
    def __new__(cls, value):
        if value < -273.15:
            raise ValueError("abaixo do zero absoluto")
        return super().__new__(cls, value)


print(Celsius(21.5) + 1, type(Celsius(21.5) + 1).__name__)
try:
    Celsius(-300)
except ValueError as error:
    print("ValueError:", error)


# __init__ não pode devolver nada
class BadInit:
    def __init__(self):
        return 5


try:
    BadInit()
except TypeError as error:
    print("TypeError:", error)
