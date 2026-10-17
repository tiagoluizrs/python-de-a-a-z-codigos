"""Cada sintaxe do Python é, por baixo, a chamada de um método especial."""
import operator


class Bag:
    def __init__(self, *things):
        self.things = list(things)

    def __len__(self):
        print("    -> __len__")
        return len(self.things)

    def __getitem__(self, index):
        print(f"    -> __getitem__({index!r})")
        return self.things[index]

    def __contains__(self, item):
        print(f"    -> __contains__({item!r})")
        return item in self.things

    def __iter__(self):
        print("    -> __iter__")
        return iter(self.things)

    def __bool__(self):
        print("    -> __bool__")
        return bool(self.things)

    def __call__(self, *args):
        print(f"    -> __call__{args}")
        return "chamado"

    def __repr__(self):
        return f"Bag{tuple(self.things)!r}"


bag = Bag("a", "b", "c")
steps = [
    ("len(bag)", lambda: len(bag)),
    ("bag[1]", lambda: bag[1]),
    ("bag[0:2]", lambda: bag[0:2]),
    ("'a' in bag", lambda: "a" in bag),
    ("list(bag)", lambda: list(bag)),
    ("bool(bag)", lambda: bool(bag)),
    ("if bag:", lambda: ("sim" if bag else "não")),
    ("bag(1, 2)", lambda: bag(1, 2)),
    ("repr(bag)", lambda: repr(bag)),
]
for label, action in steps:
    print(f"{label:<12}")
    print("   =", action())

# O módulo operator expõe as mesmas operações como funções
print(operator.length_hint(bag), operator.contains(bag, "b"),
      operator.getitem(bag, 2))

# O Python busca o método no TIPO, não na instância
bag.__len__ = lambda: 999
print("len(bag) usa a classe:", len(bag))
