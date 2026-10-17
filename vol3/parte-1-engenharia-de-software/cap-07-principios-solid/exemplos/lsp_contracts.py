"""L: Substituição de Liskov. Onde se espera a classe base, QUALQUER subclasse deve servir, sem surpresa. E como PROVAR isso: testes de contrato."""
from collections import UserDict
from collections.abc import MutableMapping


# --- 1. o clássico: Quadrado herda de Retângulo e quebra o contrato ---
class Rectangle:
    def __init__(self, w, h):
        self.w, self.h = w, h

    def set_width(self, w):
        self.w = w

    def set_height(self, h):
        self.h = h

    def area(self):
        return self.w * self.h


class Square(Rectangle):
    def set_width(self, w):
        self.w = self.h = w                     # "um quadrado tem lados iguais": mudar a largura muda a altura

    def set_height(self, h):
        self.w = self.h = h


def stretch(shape: Rectangle) -> int:
    """Código escrito contra o contrato de Rectangle: largura e altura são independentes."""
    shape.set_width(5)
    shape.set_height(2)
    return shape.area()                         # o contrato diz: 10


print("Retângulo: stretch ->", stretch(Rectangle(1, 1)), "(esperado 10)")
print("Quadrado : stretch ->", stretch(Square(1, 1)), "(esperado 10: a subclasse QUEBROU o contrato; 'é um' não bastou)")

# --- 2. a versão que respeita: tipos separados, comportamento imutável ---
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    w: float
    h: float

    def area(self):
        return self.w * self.h

    def with_width(self, w):
        return Rect(w, self.h)


@dataclass(frozen=True)
class Sq:
    side: float

    def area(self):
        return self.side**2


print("com valores imutáveis, Quadrado e Retângulo não precisam herdar um do outro: ", Rect(5, 2).area(), Sq(3).area())

# --- 3. a pegadinha do Python: subclasses de tipos embutidos que 'validam' ---
class PositiveDict(dict):
    """Quer garantir valores positivos: sobrescreve __setitem__... e acha que acabou."""

    def __setitem__(self, key, value):
        if value <= 0:
            raise ValueError("só valores positivos")
        super().__setitem__(key, value)


d = PositiveDict()
d["a"] = 1
try:
    d["b"] = -1
except ValueError as error:
    print("\n__setitem__ valida:", error)
d.update({"c": -5})                              # update do dict em C NÃO chama o seu __setitem__
d.setdefault("e", -7)                            # setdefault também não
d2 = PositiveDict({"x": -1})                     # nem o construtor
print("mas o contrato furou por 3 caminhos:", dict(d), dict(d2))


class SafeDict(UserDict):
    """UserDict e MutableMapping (collections.abc) implementam tudo em Python, em cima de __setitem__: a regra vale em todos os caminhos."""

    def __setitem__(self, key, value):
        if value <= 0:
            raise ValueError("só valores positivos")
        super().__setitem__(key, value)


s = SafeDict()
for label, action in [("[]=", lambda: s.__setitem__("a", -1)), ("update", lambda: s.update({"b": -1})), ("setdefault", lambda: s.setdefault("c", -1)),
                      ("construtor", lambda: SafeDict({"d": -1}))]:
    try:
        action()
        print(f"  SafeDict.{label}: ACEITOU o valor negativo")
    except ValueError:
        print(f"  SafeDict.{label}: recusou")


# --- 4. o teste de CONTRATO: a mesma bateria de testes roda contra TODA implementação da interface ---
def mapping_contract(factory) -> list[str]:
    """O que qualquer MutableMapping promete. Devolve as violações (lista vazia = honra o contrato)."""
    violations = []
    m = factory()
    m["a"] = 1
    if m["a"] != 1 or len(m) != 1 or "a" not in m:
        violations.append("set/get/len/in")
    m.update({"b": 2})
    if sorted(m) != ["a", "b"]:
        violations.append("update")
    if m.setdefault("c", 3) != 3 or m["c"] != 3:
        violations.append("setdefault")
    del m["a"]
    if "a" in m:
        violations.append("del")
    if m.pop("b") != 2 or "b" in m:
        violations.append("pop")
    try:
        m["zzz"]
        violations.append("KeyError esperado")
    except KeyError:
        pass
    return violations


def positive_contract(factory) -> list[str]:
    """A promessa EXTRA da subclasse: nenhum caminho aceita valor não positivo."""
    out = []
    for name, action in [("[]=", lambda m: m.__setitem__("x", -1)), ("update", lambda m: m.update(x=-1)), ("setdefault", lambda m: m.setdefault("x", -1))]:
        m = factory()
        try:
            action(m)
            out.append(f"{name} aceitou -1")
        except ValueError:
            pass
    return out


print("\nteste de contrato (mesmos testes, implementações diferentes):")
for label, factory in [("dict", dict), ("UserDict", UserDict), ("PositiveDict", PositiveDict), ("SafeDict", SafeDict)]:
    print(f"  {label:<13} MutableMapping: {mapping_contract(factory) or 'ok'} | positivos: {positive_contract(factory) if label in ('PositiveDict', 'SafeDict') else '-'}")
print(f"  SafeDict é um MutableMapping de verdade? {isinstance(SafeDict(), MutableMapping)}")


# --- 5. outras violações comuns em Python ---
class Bird:
    def fly(self):
        return "voando"


class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("pinguins não voam")      # a subclasse "desativa" um método herdado: o chamador explode


def migrate(birds):
    return [b.fly() for b in birds]


try:
    migrate([Bird(), Penguin()])
except NotImplementedError as error:
    print("\nsubclasse que levanta NotImplementedError em um método herdado:", error, "(quem usa Bird não esperava isso)")
print("a saída: Bird sem fly(); FlyingBird(Bird) com fly(); Penguin herda só de Bird (a hierarquia reflete o que cada um PODE fazer)")

print("\nregras de Liskov, em português: a subclasse pode (1) pedir MENOS do chamador, (2) prometer MAIS, (3) nunca lançar exceções novas,")
print("(4) nunca contradizer o que a classe base documenta; e tem que passar nos MESMOS testes de contrato que a base")
