"""functools.cached_property: um descritor SEM dados que se cacheia."""
import functools
import timeit


class Report:
    def __init__(self):
        self.computations = 0

    @functools.cached_property
    def total(self):
        self.computations += 1
        return sum(range(1000))

    @property
    def total_property(self):
        self.computations += 1
        return sum(range(1000))


r = Report()
print(vars(r))
print(r.total, r.total, r.computations, "total" in vars(r))     # calculou uma vez e guardou
del r.total                                                       # invalida o cache
print(r.total, r.computations)
r.total = 7                                                       # é atribuível (sem dados)
print(r.total)

# Por que funciona: depois do 1º acesso o valor está no __dict__ da instância,
# que VENCE o descritor sem dados. É o mecanismo da precedência.
print(type(Report.__dict__["total"]).__name__, hasattr(Report.__dict__["total"], "__set__"))


# Limitação: exige __dict__
class Slotted:
    __slots__ = ("x",)

    @functools.cached_property
    def y(self):
        return 1


try:
    Slotted().y
except TypeError as error:
    print("TypeError:", error)


# Custo
class Plain:
    def __init__(self):
        self.value = 1
        self._v = 1

    @property
    def prop(self):
        return self._v

    @functools.cached_property
    def cached(self):
        return 1


obj = Plain()
obj.cached                                                        # aquece o cache
for label, statement in (("atributo comum", "obj.value"), ("property", "obj.prop"),
                         ("cached_property (cacheado)", "obj.cached")):
    seconds = min(timeit.repeat(statement, globals={"obj": obj}, number=1_000_000,
                                repeat=5)) / 1_000_000
    print(f"{label:<28}{seconds * 1e9:6.1f} ns")
