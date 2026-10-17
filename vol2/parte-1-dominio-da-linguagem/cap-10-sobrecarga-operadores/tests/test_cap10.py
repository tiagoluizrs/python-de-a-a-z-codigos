import math

import pytest


def test_vec_arithmetic(load_exercise):
    Vec = load_exercise("ex01_vec").Vec
    a, b = Vec(1, 2), Vec(3, 4)
    assert a + b == Vec(4, 6) and b - a == Vec(2, 2)
    assert a * 3 == Vec(3, 6) and 3 * a == Vec(3, 6) and b / 2 == Vec(1.5, 2.0)
    assert -a == Vec(-1, -2) and abs(b) == 5.0 and a @ b == 11
    assert repr(a) == "Vec(1, 2)"
    assert math.isclose(abs(Vec(1, 1)), math.sqrt(2))


def test_vec_sum_bool_hash(load_exercise):
    Vec = load_exercise("ex01_vec").Vec
    assert sum([Vec(1, 1), Vec(2, 2), Vec(3, 3)]) == Vec(6, 6)
    assert not Vec(0, 0) and Vec(0, 1)
    assert Vec(1, 2) != (1, 2) and Vec(1, 2) == Vec(1, 2)
    assert {Vec(1, 2): "x"}[Vec(1, 2)] == "x"


def test_vec_unsupported(load_exercise):
    Vec = load_exercise("ex01_vec").Vec
    v = Vec(1, 2)
    for action in (lambda: v + 1, lambda: v * v, lambda: "x" + v, lambda: v < v,
                   lambda: v / "a", lambda: v @ 3):
        with pytest.raises(TypeError):
            action()


def test_version_ordering(load_exercise):
    Version = load_exercise("ex02_version").Version
    assert Version("1.9.0") < Version("1.10.0")
    assert Version("1.10.2") > Version("1.10.1") >= Version("1.10.1")
    assert Version("2") == Version("2.0.0") and hash(Version("2")) == hash(Version("2.0.0"))
    assert Version("1.2") < "1.10" and Version("1.2") == "1.2.0"
    assert repr(Version("1.10.2")) == "Version('1.10.2')"
    versions = [Version(v) for v in ("1.10", "1.2", "1.9.1", "0.9")]
    assert [v.text for v in sorted(versions)] == ["0.9", "1.2", "1.9.1", "1.10"]
    assert max(versions).text == "1.10"


def test_version_other_types(load_exercise):
    Version = load_exercise("ex02_version").Version
    assert Version("1.0") != 1.0
    with pytest.raises(TypeError):
        Version("1.0") < 5


def test_poly_arithmetic(load_exercise):
    Poly = load_exercise("ex03_poly").Poly
    x = Poly([0, 1])
    assert (x + 1) ** 2 == Poly([1, 2, 1])
    assert Poly([1, 2]) * Poly([1, -2]) == Poly([1, 0, -4])
    assert 2 * Poly([1, 2]) == Poly([2, 4]) and 1 + Poly([1]) == Poly([2])
    assert Poly([5, 1]) - Poly([5, 1]) == Poly([]) and not Poly([5]) - 5
    assert 10 - Poly([1, 1]) == Poly([9, -1])
    assert -Poly([1, -2]) == Poly([-1, 2])
    assert Poly([1, 0, 0]) == Poly([1]) and Poly([1, 0]).degree == 0
    assert Poly([]).degree == -1 and repr(Poly([1, 2, 3])) == "Poly([1, 2, 3])"


def test_poly_call_and_errors(load_exercise):
    Poly = load_exercise("ex03_poly").Poly
    p = Poly([1, 2, 3])                      # 1 + 2x + 3x^2
    assert p(0) == 1 and p(2) == 17 and p(-1) == 2
    assert Poly([]) (5) == 0
    with pytest.raises(TypeError):
        Poly([1]) + "a"
    with pytest.raises(TypeError):
        Poly([1]) ** -1


def test_money_arithmetic(load_exercise):
    module = load_exercise("ex04_money")
    Money, D = module.Money, __import__("decimal").Decimal
    a, b = Money(D("10.50"), "BRL"), Money(D("2.25"), "BRL")
    assert a + b == Money(D("12.75"), "BRL") and a - b == Money(D("8.25"), "BRL")
    assert a * 2 == Money(D("21.00"), "BRL") and D("0.5") * a == Money(D("5.25"), "BRL")
    assert a / 2 == Money(D("5.25"), "BRL") and a / b == D("10.50") / D("2.25")
    assert -b == Money(D("-2.25"), "BRL") and abs(-b) == b
    assert sum([a, b, b]) == Money(D("15.00"), "BRL")
    assert not Money(D("0"), "BRL") and a


def test_money_currency_errors_and_order(load_exercise):
    module = load_exercise("ex04_money")
    Money, Mismatch, D = module.Money, module.CurrencyMismatch, __import__("decimal").Decimal
    brl, usd = Money(D("1"), "BRL"), Money(D("1"), "USD")
    with pytest.raises(Mismatch):
        brl + usd
    with pytest.raises(Mismatch):
        brl < usd
    assert brl != usd and brl == Money(D("1.00"), "BRL")
    assert Money(D("1"), "BRL") < Money(D("2"), "BRL") <= Money(D("2"), "BRL")
    assert max(Money(D("1"), "BRL"), Money(D("5"), "BRL")).amount == 5
    assert hash(brl) == hash(Money(D("1.0"), "BRL"))
    with pytest.raises(TypeError):
        brl + 1


def test_pipeline(load_exercise):
    Step = load_exercise("ex05_pipeline").Step
    clean = Step(str.strip) | str.lower | Step(lambda s: s.replace(" ", "-"), "dash")
    assert clean("  Ola Mundo ") == "ola-mundo"
    assert repr(Step(str.strip) | str.lower) == "Step(strip | lower)"
    assert "  Ola " >> (Step(str.strip) | str.lower) == "ola"
    assert (len | Step(lambda n: n * 2))("abc") == 6
    with pytest.raises(TypeError):
        Step(str.strip) | 5
