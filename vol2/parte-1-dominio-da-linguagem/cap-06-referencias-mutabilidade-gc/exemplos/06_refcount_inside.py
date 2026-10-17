"""Contagem de referências: quando sobe, quando desce, quando morre."""
import sys
import weakref


class Tracked:
    def __init__(self, name: str) -> None:
        self.name = name


def announce(obj: Tracked) -> None:
    weakref.finalize(obj, print, f"  [morreu] {obj.name}")


def demo_counts() -> None:
    a = Tracked("a")
    print("um nome        :", sys.getrefcount(a))
    b = a
    print("segundo nome   :", sys.getrefcount(a))
    box = [a]
    print("dentro de lista:", sys.getrefcount(a))
    mapping = {"k": a}
    print("dentro de dict :", sys.getrefcount(a))
    del b, box, mapping
    print("depois do del  :", sys.getrefcount(a))


demo_counts()
print("--- no escopo global, o mesmo código dá +1")
g = Tracked("g")
print("global         :", sys.getrefcount(g))
del g

print("--- morte imediata")
x = Tracked("x")
announce(x)
y = x
print("del x (y ainda segura)")
del x
print("del y (último nome)")
del y
print("depois do del y")

print("--- reatribuir também solta a referência")
z = Tracked("z1")
announce(z)
z = Tracked("z2")
announce(z)
print("fim do bloco")

print("--- retorno de função e temporários")


def make() -> Tracked:
    local = Tracked("local")
    announce(local)
    return local       # a referência sobe para o chamador


kept = make()
print("kept vivo:", kept.name)
t = Tracked("temp2")
announce(t)
t = None             # solta o único nome: morre aqui
print("fim do script")
