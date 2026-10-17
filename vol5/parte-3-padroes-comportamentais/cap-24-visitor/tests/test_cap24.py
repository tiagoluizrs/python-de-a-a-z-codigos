import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


# ---------- ex01 ----------
def sample(m):
    # 2 + x * -(y + 1)
    return m.Add(m.Num(2), m.Mul(m.Var("x"), m.Neg(m.Add(m.Var("y"), m.Num(1)))))


def test_evaluator(load_exercise):
    m = load_exercise("ex01_expr_visitors")
    assert sample(m).accept(m.Evaluator({"x": 4, "y": 2})) == 2 + 4 * -(2 + 1)
    assert m.Num(7).accept(m.Evaluator({})) == 7 and m.Neg(m.Num(3)).accept(m.Evaluator({})) == -3
    with pytest.raises(KeyError, match="variável indefinida: y"):
        sample(m).accept(m.Evaluator({"x": 1}))
    e = m.Evaluator({"x": 2})
    assert m.Add(m.Var("x"), m.Var("x")).accept(e) == 4 and m.Mul(m.Var("x"), m.Num(5)).accept(e) == 10


def test_printer_minimal_parentheses(load_exercise):
    m = load_exercise("ex01_expr_visitors")
    x, y = m.Var("x"), m.Var("y")
    show = lambda node: node.accept(m.Printer())
    assert show(sample(m)) == "2 + x * -(y + 1)"
    assert show(m.Mul(m.Add(x, m.Num(3)), m.Num(2))) == "(x + 3) * 2"
    assert show(m.Neg(m.Add(x, m.Num(1)))) == "-(x + 1)"
    assert show(m.Add(m.Num(2), m.Mul(x, y))) == "2 + x * y"
    assert show(m.Neg(m.Mul(m.Num(2), x))) == "-(2 * x)"
    assert show(m.Mul(m.Neg(x), y)) == "-x * y" and show(m.Neg(m.Neg(x))) == "--x"
    assert show(m.Add(m.Add(x, y), m.Num(1))) == "x + y + 1" and show(m.Add(x, m.Add(y, m.Num(1)))) == "x + y + 1"
    assert show(m.Mul(x, m.Mul(y, m.Num(2.5)))) == "x * y * 2.5" and show(m.Num(7)) == "7" and show(x) == "x"


def test_variable_collector_and_depth(load_exercise):
    m = load_exercise("ex01_expr_visitors")
    assert sample(m).accept(m.VariableCollector()) == ["x", "y"]
    assert m.Add(m.Var("b"), m.Mul(m.Var("a"), m.Var("b"))).accept(m.VariableCollector()) == ["a", "b"]
    assert m.Num(1).accept(m.VariableCollector()) == []
    assert m.Num(1).accept(m.Depth()) == 1 and m.Var("x").accept(m.Depth()) == 1
    assert sample(m).accept(m.Depth()) == 5
    assert m.Neg(m.Neg(m.Num(1))).accept(m.Depth()) == 3


def test_count_visitor_has_state(load_exercise):
    m = load_exercise("ex01_expr_visitors")
    c = m.CountVisitor()
    assert sample(m).accept(c) is None
    assert c.counts == {"Num": 2, "Var": 2, "Add": 2, "Mul": 1, "Neg": 1}
    m.Neg(m.Var("z")).accept(c)
    assert c.counts["Var"] == 3 and c.counts["Neg"] == 2 and c.counts["Num"] == 2
    assert m.CountVisitor().counts == {}


# ---------- ex02 ----------
def test_area_and_perimeter(load_exercise):
    m = load_exercise("ex02_singledispatch_shapes")
    assert m.area(m.Circle(2)) == pytest.approx(math.pi * 4) and m.perimeter(m.Circle(2)) == pytest.approx(4 * math.pi)
    assert m.area(m.Rect(3, 4)) == 12 and m.perimeter(m.Rect(3, 4)) == 14
    assert m.area(m.Triangle(3, 4, 5)) == pytest.approx(6) and m.perimeter(m.Triangle(3, 4, 5)) == 12
    group = m.Group([m.Rect(1, 2), m.Group([m.Rect(2, 2), m.Circle(1)])])
    assert m.area(group) == pytest.approx(2 + 4 + math.pi) and m.perimeter(group) == pytest.approx(6 + 8 + 2 * math.pi)
    assert m.area(m.Group([])) == 0 and m.perimeter(m.Group(())) == 0


def test_describe_and_count(load_exercise):
    m = load_exercise("ex02_singledispatch_shapes")
    assert m.describe(m.Circle(2.0)) == "círculo de raio 2" and m.describe(m.Circle(1.5)) == "círculo de raio 1.5"
    assert m.describe(m.Rect(3, 4)) == "retângulo 3x4" and m.describe(m.Rect(3, 3)) == "quadrado de lado 3"
    assert m.describe(m.Triangle(3, 4, 5)) == "triângulo 3-4-5"
    group = m.Group([m.Rect(3, 3), m.Group([m.Circle(1), m.Triangle(3, 4, 5)])])
    assert m.describe(group) == "grupo de 2 formas: quadrado de lado 3; grupo de 2 formas: círculo de raio 1; triângulo 3-4-5"
    assert m.count_shapes(group) == 3 and m.count_shapes(m.Circle(1)) == 1 and m.count_shapes(m.Group([])) == 0
    assert m.count_shapes(m.Group([m.Group([m.Group([m.Rect(1, 1)])]), m.Rect(1, 1)])) == 2


def test_unknown_type_and_dispatch_is_extensible(load_exercise):
    m = load_exercise("ex02_singledispatch_shapes")
    for fn in (m.area, m.perimeter, m.describe, m.count_shapes):
        with pytest.raises(TypeError, match="forma desconhecida: str"):
            fn("quadrado")
        assert hasattr(fn, "register") and hasattr(fn, "dispatch")

    class Square:
        def __init__(self, side):
            self.side = side

    m.area.register(Square, lambda s: s.side ** 2)
    assert m.area(Square(3)) == 9
    assert m.area(m.Group([m.Rect(1, 1), Square(2)])) == 5            # a extensão vale dentro dos grupos
    with pytest.raises(TypeError, match="forma desconhecida: Square"):
        m.perimeter(Square(3))


def test_shape_validation_is_given(load_exercise):
    m = load_exercise("ex02_singledispatch_shapes")
    with pytest.raises(ValueError, match="medida inválida"):
        m.Circle(0)
    with pytest.raises(ValueError, match="triângulo inválido"):
        m.Triangle(1, 2, 3)
    assert isinstance(m.Group([m.Circle(1)]).shapes, tuple)


# ---------- ex03 ----------
def test_simplify_rules(load_exercise):
    m = load_exercise("ex03_simplifier")
    x, y = m.Var("x"), m.Var("y")
    s = m.simplify
    assert s(m.Add(x, m.Num(0))) == x and s(m.Add(m.Num(0), x)) == x
    assert s(m.Mul(m.Num(1), x)) == x and s(m.Mul(x, m.Num(1))) == x
    assert s(m.Mul(x, m.Num(0))) == m.Num(0) and s(m.Mul(m.Num(0), m.Add(x, y))) == m.Num(0)
    assert s(m.Neg(m.Neg(x))) == x and s(m.Neg(m.Num(5))) == m.Num(-5)
    assert s(m.Add(m.Num(2), m.Num(3))) == m.Num(5) and s(m.Mul(m.Num(2), m.Num(3))) == m.Num(6)
    assert s(m.Add(x, x)) == m.Add(x, x) and s(m.Add(x, y)) == m.Add(x, y) and s(x) == x and s(m.Num(4)) == m.Num(4)


def test_simplify_bottom_up_to_fixed_point(load_exercise):
    m = load_exercise("ex03_simplifier")
    x, y = m.Var("x"), m.Var("y")
    messy = m.Add(m.Mul(m.Num(1), x), m.Mul(m.Num(0), m.Add(y, m.Num(9))))
    assert m.simplify(messy) == x
    assert m.simplify(m.Mul(m.Add(m.Num(1), m.Num(-1)), x)) == m.Num(0)
    assert m.simplify(m.Neg(m.Add(m.Num(1), m.Num(2)))) == m.Num(-3)
    assert m.simplify(m.Neg(m.Neg(m.Add(x, m.Num(0))))) == x
    deep = m.Add(m.Add(m.Add(m.Num(0), m.Num(0)), m.Num(0)), m.Mul(m.Num(1), m.Mul(m.Num(1), y)))
    assert m.simplify(deep) == y
    assert m.simplify(m.Add(m.Mul(m.Num(2), m.Num(3)), x)) == m.Add(m.Num(6), x)


def test_derive(load_exercise):
    m = load_exercise("ex03_simplifier")
    x, y = m.Var("x"), m.Var("y")
    assert m.derive(m.Num(5), "x") == m.Num(0) and m.derive(x, "x") == m.Num(1) and m.derive(y, "x") == m.Num(0)
    assert m.derive(m.Mul(x, x), "x") == m.Add(x, x)
    assert m.derive(m.Add(m.Mul(m.Num(3), x), m.Num(5)), "x") == m.Num(3)
    assert m.derive(m.Mul(x, y), "y") == x and m.derive(m.Mul(x, y), "z") == m.Num(0)
    assert m.derive(m.Neg(x), "x") == m.Num(-1)
    assert m.derive(m.Mul(m.Mul(x, x), x), "x") == m.Add(m.Mul(m.Add(x, x), x), m.Mul(x, x))
    at_two = m.simplify(m.substitute(m.derive(m.Mul(x, x), "x"), {"x": 2}))
    assert at_two == m.Num(4)


def test_substitute(load_exercise):
    m = load_exercise("ex03_simplifier")
    x, y = m.Var("x"), m.Var("y")
    tree = m.Add(m.Mul(x, y), m.Neg(x))
    assert m.substitute(tree, {"x": 2}) == m.Add(m.Mul(m.Num(2), y), m.Neg(m.Num(2)))
    assert m.substitute(tree, {}) == tree and m.substitute(tree, {"z": 1}) == tree
    assert m.substitute(m.Add(m.Num(2), m.Num(3)), {"x": 1}) == m.Add(m.Num(2), m.Num(3))
    assert m.substitute(x, {"x": 0}) == m.Num(0)
    assert tree == m.Add(m.Mul(x, y), m.Neg(x))


# ---------- ex04 ----------
def test_function_names(load_exercise):
    m = load_exercise("ex04_ast_tools")
    source = (
        "def a():\n    def inner():\n        pass\n\n"
        "class C:\n    def method(self):\n        pass\n\n    async def amethod(self):\n        pass\n\n"
        "def b():\n    return lambda: 1\n"
    )
    assert m.function_names(source) == ["a", "inner", "method", "amethod", "b"]
    assert m.function_names("x = 1") == []
    with pytest.raises(SyntaxError):
        m.function_names("def :")


def test_imported_modules(load_exercise):
    m = load_exercise("ex04_ast_tools")
    source = "import os.path\nimport b, a\nfrom collections.abc import Mapping\nfrom . import x\nfrom .pkg import y\nimport os\n\ndef f():\n    import json\n"
    assert m.imported_modules(source) == ["a", "b", "collections", "json", "os"]
    assert m.imported_modules("x = 1") == [] and m.imported_modules("from .. import z") == []
    assert m.imported_modules("import numpy as np\nfrom numpy import linalg") == ["numpy"]


def test_max_loop_depth(load_exercise):
    m = load_exercise("ex04_ast_tools")
    assert m.max_loop_depth("x = 1") == 0 and m.max_loop_depth("y = [i for i in range(3)]") == 0
    assert m.max_loop_depth("for i in a:\n    for j in b:\n        while c:\n            pass\nfor z in w:\n    pass\n") == 3
    assert m.max_loop_depth("for a in b:\n    def f():\n        for c in d:\n            pass\n") == 2
    assert m.max_loop_depth("async def f():\n    async for a in b:\n        for c in a:\n            pass\n") == 2
    assert m.max_loop_depth("while x:\n    pass\nwhile y:\n    pass\n") == 1
    assert m.max_loop_depth("for a in b:\n    x = [i for i in a for j in i]\n") == 1


def test_fold_constants(load_exercise):
    m = load_exercise("ex04_ast_tools")
    f = m.fold_constants
    assert f("x = 2 * 3 + y") == "x = 6 + y" and f("print(1 + 2 * 3)") == "print(7)"
    assert f("10 - 4 - 3") == "3" and f("(1 + 2) * (3 + 4)") == "21" and f("2 - 5") == "-3"
    assert f("def f():\n    return 60 * 60 * 24") == "def f():\n    return 86400"
    assert f("y + 1 + 2") == "y + 1 + 2" and f("5 - 8 * y") == "5 - 8 * y"
    assert f("True + 1") == "True + 1" and f("1.5 + 2") == "1.5 + 2" and f("'a' + 'b'") == "'a' + 'b'"
    assert f("2 ** 3") == "2 ** 3" and f("7 // 2") == "7 // 2" and f("x = 1") == "x = 1"
    with pytest.raises(SyntaxError):
        f("x = = 1")


# ---------- exemplos ----------
@pytest.mark.parametrize("name", ["visitor_classico", "visitor_pythonico"])
def test_examples_run(name):
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=ROOT / "exemplos", capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
