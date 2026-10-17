"""Introspecção: inspect, getattr, annotations, signature."""
import inspect
import types
from dataclasses import dataclass


@dataclass
class Item:
    """Um item."""
    name: str
    qty: int = 1

    def total(self, price: float, *, discount: float = 0.0) -> float:
        """Calcula o total."""
        return self.qty * price * (1 - discount)


sig = inspect.signature(Item.total)
print(sig, "|", [(p.name, p.kind.name, p.default) for p in sig.parameters.values()])
print(inspect.get_annotations(Item), inspect.get_annotations(Item.total))
print(inspect.getdoc(Item), "|", inspect.getdoc(Item.total))

# Classificar membros
members = inspect.getmembers(Item, predicate=inspect.isfunction)
print([n for n, _ in members])
print(inspect.isclass(Item), inspect.ismethod(Item(" a").total), inspect.isfunction(Item.total))

# getattr / setattr / hasattr / delattr: nomes dinâmicos
item = Item("x", 3)
for field in ("name", "qty", "missing"):
    print(field, getattr(item, field, "<ausente>"))
setattr(item, "qty", 10)
print(item.qty)

# dir() x vars() x __dict__
print([n for n in dir(item) if not n.startswith("_")], vars(item))

# Código-fonte (quando disponível)
print(inspect.getsource(Item.total).splitlines()[0])
print(inspect.getsourcefile(Item).endswith("introspection.py"))

# Quem chamou? a pilha
def whoami():
    return inspect.stack()[1].function


def caller():
    return whoami()


print(caller())

# types: criar objetos de função/módulo/namespace dinamicamente
ns = types.SimpleNamespace(a=1, b=2)
print(ns, ns.a)
mod = types.ModuleType("fake")
mod.value = 42
print(mod.value, mod.__name__)
print(types.FunctionType, type(lambda: 0) is types.FunctionType)


# Código de função: __code__
def f(a, b):
    c = a + b
    return c


code = f.__code__
print(code.co_varnames, code.co_argcount, code.co_name)
