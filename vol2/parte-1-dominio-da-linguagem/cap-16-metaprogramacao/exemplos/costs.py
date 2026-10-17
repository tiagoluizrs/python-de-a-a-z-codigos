"""Custos da metaprogramação: criar classes, instanciar com metaclasse."""
import timeit
from dataclasses import dataclass


def make_plain():
    class P:
        def __init__(self, a, b):
            self.a, self.b = a, b
    return P


def make_type():
    return type("P", (), {"__init__": lambda self, a, b: None})


def make_dataclass_():
    @dataclass
    class P:
        a: int
        b: int
    return P


print("criar a classe (uma vez, na definição):")
for label, fn in [("class statement", make_plain), ("type(...)", make_type), ("@dataclass", make_dataclass_)]:
    seconds = min(timeit.repeat(fn, number=2000, repeat=5)) / 2000
    print(f"  {label:<16}{seconds * 1e6:8.1f} us")


class Plain:
    def __init__(self):
        self.a = 1


class Meta(type):
    pass


class WithMeta(metaclass=Meta):
    def __init__(self):
        self.a = 1


class CallMeta(type):
    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class WithCallMeta(metaclass=CallMeta):
    def __init__(self):
        self.a = 1


class WithInitSub:
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)


print("instanciar (ns):")
ns = dict(Plain=Plain, WithMeta=WithMeta, WithCallMeta=WithCallMeta)
for label, statement in [("sem metaclasse", "Plain()"), ("metaclasse sem __call__", "WithMeta()"),
                         ("metaclasse com __call__", "WithCallMeta()")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=500_000, repeat=5)) / 500_000
    print(f"  {label:<26}{seconds * 1e9:7.1f} ns")
