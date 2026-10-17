"""Como o Python resolve `a + b`: __add__, __radd__ e NotImplemented."""


class Left:
    def __add__(self, other):
        print("  Left.__add__")
        return NotImplemented              # "não sei lidar com isso"


class Right:
    def __radd__(self, other):
        print("  Right.__radd__")
        return "resultado do __radd__"


print("1) a.__add__ recusa; b.__radd__ resolve")
print("  =", Left() + Right())


class Quiet:
    pass


print("2) ninguém sabe fazer")
try:
    Left() + Quiet()
except TypeError as error:
    print("  TypeError:", error)


print("3) `1 + obj`: int não conhece Right, então vai direto ao __radd__")
print("  =", 1 + Right())


# Regra da subclasse: se b é SUBCLASSE de a e redefine o método refletido,
# o __radd__ de b é tentado ANTES do __add__ de a
class Base:
    def __add__(self, other):
        print("  Base.__add__")
        return "base"

    def __radd__(self, other):
        print("  Base.__radd__")
        return "base-r"


class Child(Base):
    def __radd__(self, other):
        print("  Child.__radd__")
        return "child-r"


print("4) Base() + Child(): a subclasse tem prioridade")
print("  =", Base() + Child())
print("5) Child() + Base(): ordem normal")
print("  =", Child() + Base())


# NotImplemented NÃO é NotImplementedError
print(type(NotImplemented).__name__, bool.__name__)
try:
    raise NotImplemented
except TypeError as error:
    print("raise NotImplemented ->", error)
