import math
from collections.abc import MutableMapping

import pytest


def test_shapes_polymorphism(load_exercise):
    module = load_exercise("ex01_shapes")
    circle, rect, square = module.Circle(1), module.Rect(2, 3), module.Square(2)
    assert round(circle.area(), 4) == round(math.pi, 4)
    assert rect.area() == 6 and square.area() == 4
    assert rect.describe() == "Rect com área 6.00"
    assert square.describe() == "Square com área 4.00"
    assert isinstance(square, module.Rect) and square.side == 2
    with pytest.raises(NotImplementedError):
        module.Shape().area()


def test_shapes_ordering(load_exercise):
    module = load_exercise("ex01_shapes")
    shapes = [module.Rect(2, 3), module.Circle(1), module.Square(1.5)]
    assert [type(s).__name__ for s in sorted(shapes)] == ["Square", "Circle", "Rect"]
    assert type(max(shapes)).__name__ == "Rect"


def _name_list(classes):
    return [c.__name__ for c in classes]


def test_c3_matches_python(load_exercise):
    c3 = load_exercise("ex02_c3").c3_linearization

    class A: pass
    class B(A): pass
    class C(A): pass
    class D(B, C): pass
    assert c3(D) == list(D.__mro__)
    assert _name_list(c3(D)) == ["D", "B", "C", "A", "object"]

    class O: pass
    class A1(O): pass
    class B1(O): pass
    class C1(O): pass
    class D1(O): pass
    class E1(O): pass
    class K1(A1, B1, C1): pass
    class K2(D1, B1, E1): pass
    class K3(D1, A1): pass
    class Z(K1, K2, K3): pass
    assert c3(Z) == list(Z.__mro__)
    assert c3(object) == [object]
    assert c3(int) == list(int.__mro__)


class FakeClass:
    """Imita só o que o algoritmo usa: ``__bases__``."""

    def __init__(self, name, bases=()):
        self.__name__, self.__bases__ = name, tuple(bases)

    def __repr__(self):
        return self.__name__


def test_c3_inconsistent(load_exercise):
    c3 = load_exercise("ex02_c3").c3_linearization
    x = FakeClass("X")
    y = FakeClass("Y", [x])
    z = FakeClass("Z", [x, y])                 # X antes de Y, mas Y herda de X
    with pytest.raises(TypeError):
        c3(z)
    w = FakeClass("W", [y, x])
    assert c3(w) == [w, y, x]


def test_pipeline_flow(load_exercise):
    Pipeline = load_exercise("ex03_pipeline_mixins").Pipeline
    p = Pipeline()
    assert p.handle("  ola ") == "OLA!"
    assert p.trace == ["Strip", "Upper", "Exclaim", "Handler"]
    assert [c.__name__ for c in Pipeline.__mro__][:5] == [
        "Pipeline", "Strip", "Upper", "Exclaim", "Handler"]


def test_pipeline_instances_do_not_share_trace(load_exercise):
    Pipeline = load_exercise("ex03_pipeline_mixins").Pipeline
    a, b = Pipeline(), Pipeline()
    a.handle(" x ")
    assert b.trace == [] and a.trace


def test_lower_dict(load_exercise):
    LowerDict = load_exercise("ex04_lower_dict").LowerDict
    d = LowerDict({"A": 1}, B=2, HOST=3)
    d["NAME"] = 4
    d.update({"AGE": 5}, CITY=6)
    assert d.setdefault("COUNTRY", 7) == 7 and d.setdefault("country", 99) == 7
    assert sorted(d) == ["a", "age", "b", "city", "country", "host", "name"]
    assert d["name"] == d["Name"] == 4 and "HOST" in d and "host" in d
    assert d.get("CITY") == 6 and d.get("nada") is None
    assert d.pop("AGE") == 5 and "age" not in d
    del d["NAME"]
    assert "name" not in d


def test_lower_dict_types(load_exercise):
    LowerDict = load_exercise("ex04_lower_dict").LowerDict
    assert isinstance(LowerDict(), MutableMapping) and not issubclass(LowerDict, dict)
    d = LowerDict()
    d[1] = "um"
    d[("T", "x")] = "tupla"
    assert d[1] == "um" and d[("T", "x")] == "tupla"


def test_find_overrides(load_exercise):
    find = load_exercise("ex05_conflicts").find_overrides

    class Base:
        def run(self): ...
        def stop(self): ...
        data = 1

    class Mixin:
        def run(self): ...
        def log(self): ...

    class Child(Mixin, Base):
        def run(self): ...
        def __init__(self): ...

    result = find(Child)
    assert result == {"run": ["Child", "Mixin", "Base"]}
    assert find(Base) == {}
