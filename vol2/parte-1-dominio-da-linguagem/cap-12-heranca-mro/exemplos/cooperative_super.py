"""super() não é "o pai": é "o próximo na ordem do MRO da instância"."""


class Base:
    def __init__(self, **kwargs):
        print("  Base.__init__", kwargs)
        super().__init__()                 # o próximo é `object`; kwargs acabam aqui


class Named(Base):
    def __init__(self, name, **kwargs):
        print("  Named.__init__", name)
        super().__init__(**kwargs)
        self.name = name


class Aged(Base):
    def __init__(self, age, **kwargs):
        print("  Aged.__init__", age)
        super().__init__(**kwargs)
        self.age = age


class Person(Named, Aged):
    def __init__(self, **kwargs):
        print("  Person.__init__")
        super().__init__(**kwargs)


print([c.__name__ for c in Person.__mro__])
p = Person(name="Ana", age=30)
print(p.name, p.age)


# O `super()` de Named, dentro de um Person, aponta para Aged (e não para Base)
class Tracer(Named):
    pass


class Meddler(Named, Aged):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


print("--- Tracer (só Named):")
Tracer(name="x")
print("--- Meddler (Named, Aged):")
Meddler(name="x", age=1)


# Armadilha: misturar chamada explícita da base com super()
class Left(Base):
    def __init__(self, **kwargs):
        print("  Left.__init__")
        Base.__init__(self, **kwargs)      # NÃO usa o MRO


class Right(Base):
    def __init__(self, **kwargs):
        print("  Right.__init__")
        super().__init__(**kwargs)


class Both(Left, Right):
    def __init__(self, **kwargs):
        print("  Both.__init__")
        super().__init__(**kwargs)


print("--- Both (Left chama Base direto):")
Both()
print("Right.__init__ foi pulado: o MRO de Both é",
      [c.__name__ for c in Both.__mro__])
