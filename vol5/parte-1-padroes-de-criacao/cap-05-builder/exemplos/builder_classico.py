"""Builder, forma clássica (GoF): montar um objeto complexo PASSO A PASSO, separando o processo da representação."""
import ast
import inspect
import textwrap
import time
from dataclasses import dataclass, field


# --- 1. o problema: o construtor telescópico (muitos argumentos, a maioria opcionais) ---
class PizzaOld:
    def __init__(self, size, cheese=False, pepperoni=False, mushrooms=False, onions=False, olives=False, bacon=False, extra_sauce=False):
        self.size, self.toppings = size, [n for n, v in [("cheese", cheese), ("pepperoni", pepperoni), ("mushrooms", mushrooms),
                                                         ("onions", onions), ("olives", olives), ("bacon", bacon)] if v]
        self.extra_sauce = extra_sauce


p = PizzaOld("large", True, False, True, False, True, False, True)         # o que significa cada True?
print("construtor telescópico:", p.size, p.toppings, p.extra_sauce, "| a chamada não se lê: quem é o 4º booleano?")


# --- 2. o produto e o construtor (builder) com interface fluente ---
@dataclass
class Pizza:
    size: str
    dough: str = "tradicional"
    toppings: list = field(default_factory=list)
    extra_sauce: bool = False


class PizzaBuilder:
    def __init__(self):
        self._size = None
        self._dough = "tradicional"
        self._toppings = []
        self._extra_sauce = False

    def size(self, size):
        self._size = size
        return self                                          # devolver self permite encadear

    def dough(self, dough):
        self._dough = dough
        return self

    def topping(self, name):
        self._toppings.append(name)
        return self

    def extra_sauce(self):
        self._extra_sauce = True
        return self

    def build(self) -> Pizza:
        if self._size is None:
            raise ValueError("tamanho obrigatório")           # a validação mora UM lugar: o build()
        if len(self._toppings) > 5:
            raise ValueError("no máximo 5 ingredientes")
        return Pizza(self._size, self._dough, list(self._toppings), self._extra_sauce)


pizza = PizzaBuilder().size("large").topping("queijo").topping("cogumelo").extra_sauce().build()
print("\nbuilder fluente:", pizza)
try:
    PizzaBuilder().topping("queijo").build()
except ValueError as error:
    print("validação no build():", error)


# --- 3. o Diretor: uma receita pronta que usa o builder (o 'director' do GoF) ---
class PizzaDirector:
    @staticmethod
    def margherita(builder):
        return builder.size("medium").dough("fina").topping("queijo").topping("manjericão").build()

    @staticmethod
    def calabresa(builder):
        return builder.size("large").topping("calabresa").topping("cebola").build()


print("\ndiretor:", PizzaDirector.margherita(PizzaBuilder()))


# --- 4. a variante do GoF: o MESMO processo montando representações DIFERENTES ---
class TextReport:
    def __init__(self):
        self.lines = []

    def title(self, text):
        self.lines.append(text.upper())

    def item(self, text):
        self.lines.append(f"- {text}")

    def result(self):
        return "\n".join(self.lines)


class HtmlReport:
    def __init__(self):
        self.parts = []

    def title(self, text):
        self.parts.append(f"<h1>{text}</h1>")

    def item(self, text):
        self.parts.append(f"<li>{text}</li>")

    def result(self):
        return "".join(self.parts)


def build_menu(builder):                                      # o diretor: o processo é o mesmo
    builder.title("Cardápio")
    builder.item("margherita")
    builder.item("calabresa")
    return builder.result()


print("\nmesmo processo, duas representações:")
print(build_menu(TextReport()))
print(build_menu(HtmlReport()))


# --- 5. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nPizza + PizzaBuilder:", measure([Pizza, PizzaBuilder]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


print(f"montar uma pizza: builder {best(lambda: PizzaBuilder().size('large').topping('queijo').topping('cogumelo').extra_sauce().build()):5.0f} ns")
print("o builder cria um objeto intermediário e faz uma chamada por passo: custa mais que o construtor direto (veja o exemplo seguinte)")
