import io
from decimal import Decimal

import pytest


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(7, 2, (3, 1)), (-7, 2, (-3, -1)), (7, -2, (-3, 1)), (-7, -2, (3, -1)),
     (0, 5, (0, 0)), (10**30 + 1, 10**15, (10**15, 1))],
)
def test_trunc_divmod(load_exercise, a, b, expected):
    assert load_exercise("ex01_trunc_divmod").trunc_divmod(a, b) == expected


def test_trunc_divmod_by_zero(load_exercise):
    with pytest.raises(ZeroDivisionError):
        load_exercise("ex01_trunc_divmod").trunc_divmod(1, 0)


def test_split_bill(load_exercise):
    split_bill = load_exercise("ex02_split_bill").split_bill
    assert split_bill(Decimal("100.00"), 3) == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    parts = split_bill(Decimal("0.05"), 4)
    assert sum(parts) == Decimal("0.05")
    assert all(part == part.quantize(Decimal("0.01")) for part in parts)
    assert split_bill(Decimal("10.00"), 2) == [Decimal("5.00"), Decimal("5.00")]


def test_flags(load_exercise):
    m = load_exercise("ex03_permissions")
    value = m.READ | m.WRITE
    assert m.has_flag(value, m.WRITE) and not m.has_flag(value, m.EXECUTE)
    assert m.set_flag(value, m.EXECUTE) == 0b111
    assert m.clear_flag(value, m.WRITE) == 0b001
    assert m.toggle_flag(value, m.READ) == 0b010
    assert m.toggle_flag(value, m.EXECUTE) == 0b111


def test_is_power_of_two(load_exercise):
    f = load_exercise("ex03_permissions").is_power_of_two
    assert [n for n in range(0, 20) if f(n)] == [1, 2, 4, 8, 16]
    assert f(2**100) and not f(2**100 + 1) and not f(-4)


def test_coalesce(load_exercise):
    coalesce = load_exercise("ex04_coalesce").coalesce
    assert coalesce(None, 0, 5) == 0
    assert coalesce(None, "", 5) == ""
    assert coalesce(None, None, default="x") == "x"
    assert coalesce() is None
    assert coalesce([], None) == []


def test_read_in_chunks(load_exercise):
    read = load_exercise("ex05_chunks").read_in_chunks
    assert read(io.BytesIO(b"abcdefghij"), 4) == [b"abcd", b"efgh", b"ij"]
    assert read(io.BytesIO(b""), 4) == []
