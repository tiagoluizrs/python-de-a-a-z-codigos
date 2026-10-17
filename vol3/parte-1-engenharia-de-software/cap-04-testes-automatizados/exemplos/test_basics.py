"""O básico do pytest: assert simples, approx, raises, parametrize e marcas."""
import sys
from decimal import Decimal

import pytest

from pricing import apply_discount, days_until, parse_price
from datetime import date


def test_discount_basic():
    assert apply_discount(100, 10) == 90


def test_discount_rounds_to_cents():
    assert apply_discount(19.99, 15) == pytest.approx(16.99, abs=0.005)


def test_float_comparison_needs_approx():
    assert 0.1 + 0.2 != 0.3
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert [0.1 + 0.2, 1.0] == pytest.approx([0.3, 1.0])
    assert {"a": 0.1 + 0.2} == pytest.approx({"a": 0.3})


@pytest.mark.parametrize("percent", [-1, 100.01, 150])
def test_discount_rejects_invalid_percent(percent):
    with pytest.raises(ValueError, match="percentual inválido"):
        apply_discount(10, percent)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("R$ 1.234,56", Decimal("1234.56")),
        ("10,5", Decimal("10.5")),
        ("  R$0,99 ", Decimal("0.99")),
    ],
    ids=["milhar", "simples", "espacos"],
)
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_parse_price_invalid():
    with pytest.raises(ValueError) as info:
        parse_price("abc")
    assert "abc" in str(info.value)


def test_days_until_uses_injected_today():
    assert days_until(date(2026, 10, 20), today=date(2026, 10, 13)) == 7


class TestDiscountEdges:
    """Classes agrupam testes (sem herdar de nada e sem __init__)."""

    def test_zero_percent(self):
        assert apply_discount(50, 0) == 50

    def test_full_percent(self):
        assert apply_discount(50, 100) == 0


@pytest.mark.skipif(sys.platform != "win32", reason="só faz sentido no Windows")
def test_windows_only():
    assert sys.platform == "win32"


@pytest.mark.xfail(reason="bug conhecido: float binário (2.675 vira 2.67, não 2.68)", strict=True)
def test_known_bug_rounding_half_up():
    assert apply_discount(2.675, 0) == 2.68                # falha, documentado
