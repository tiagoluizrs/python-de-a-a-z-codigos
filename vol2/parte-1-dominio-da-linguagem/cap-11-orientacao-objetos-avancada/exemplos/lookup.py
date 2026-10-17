"""Atributos de instância x de classe: a ordem de busca e as armadilhas."""


class Counter:
    total = 0                       # atributo de CLASSE
    history = []                    # mutável e COMPARTILHADO (armadilha)

    def __init__(self, name):
        self.name = name            # atributo de INSTÂNCIA
        Counter.total += 1
        self.history.append(name)   # altera a lista da classe!


a, b = Counter("a"), Counter("b")
print(a.total, b.total, Counter.total)
print(a.history is b.history, a.history)
print("history" in vars(a), "name" in vars(a), sorted(vars(Counter))[-4:])


# Atribuir pela instância CRIA um atributo de instância que esconde o da classe
a.total = 100
print(a.total, b.total, Counter.total, vars(a))
del a.total
print(a.total)                      # volta a enxergar o da classe


# `self.n += 1` lê o da classe, soma e GRAVA na instância
class Hits:
    n = 0

    def hit(self):
        self.n += 1                  # self.n = self.n + 1  ->  instância
        return self.n


h1, h2 = Hits(), Hits()
h1.hit()
h1.hit()
h2.hit()
print(h1.n, h2.n, Hits.n, vars(h1))


# A correção do atributo mutável compartilhado: criar no __init__
class Fixed:
    def __init__(self):
        self.history = []


print(Fixed().history is Fixed().history)

# A ordem de busca: instância, classe, superclasses
class Base:
    level = "base"


class Child(Base):
    pass


c = Child()
print(c.level)
Child.level = "child"
print(c.level)
c.level = "instance"
print(c.level, Child.level, Base.level)
