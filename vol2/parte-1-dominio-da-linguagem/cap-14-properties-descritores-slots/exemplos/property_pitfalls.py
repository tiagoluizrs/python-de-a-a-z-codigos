"""Armadilhas clássicas de property."""

# 1) Recursão infinita: o setter atribui ao PRÓPRIO nome
class Broken:
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self.x = value                          # chama o setter de novo!


try:
    Broken().x = 1
except RecursionError as error:
    print("RecursionError:", error)


# 2) Um AttributeError DENTRO do getter dispara o __getattr__ e confunde a mensagem
class WithHook:
    def __getattr__(self, name):                # chamado quando a busca normal FALHA
        if name.startswith("dyn_"):
            return f"<{name} calculado>"
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    @property
    def total(self):
        return self.items_count * 2             # items_count NÃO existe: bug AQUI


try:
    WithHook().total
except AttributeError as error:
    print("com __getattr__ :", error)           # culpa 'total', que existe!


class Honest:
    @property
    def total(self):
        return self.items_count * 2


try:
    Honest().total
except AttributeError as error:
    print("sem __getattr__ :", error)           # culpa o atributo certo


# 3) Sobrescrever só o getter perde o setter
class Base:
    def __init__(self):
        self._v = 1

    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, value):
        self._v = value


class Child(Base):
    @property
    def v(self):                                # redefine a property inteira: sem setter
        return self._v + 100


c = Child()
print(c.v)
try:
    c.v = 5
except AttributeError as error:
    print("AttributeError:", error)


class FixedChild(Base):
    @Base.v.getter                               # copia a property, trocando só o getter
    def v(self):
        return self._v + 100


fc = FixedChild()
fc.v = 5
print(fc.v)


# 4) Nada impede de contornar: a property protege o ACESSO, não o dado
class Guarded:
    def __init__(self):
        self._secret = 1

    @property
    def secret(self):
        return self._secret


g = Guarded()
g._secret = 999
print(g.secret)
