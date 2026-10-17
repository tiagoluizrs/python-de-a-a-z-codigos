"""Gabarito do exercício 3."""
import pytest
from interest_impl import compound_interest


@pytest.mark.parametrize("principal, rate, years, periods, expected", [
    (1000, 0.05, 10, 1, 1628.894627),
    (1000, 0.05, 10, 12, 1647.009498),
    (1000, 0.05, 1, 1, 1050.0),
    (1000, 0.0, 5, 4, 1000.0),
    (0, 0.1, 3, 1, 0.0),
    (1000, 0.05, 0, 1, 1000.0),
    (200, 0.10, 2, 2, 243.101250),
])
def test_values(principal, rate, years, periods, expected):
    assert compound_interest(principal, rate, years, periods) == pytest.approx(expected, rel=1e-6)


def test_default_periods_is_one():
    assert compound_interest(100, 0.1, 2) == pytest.approx(121.0)


def test_not_rounded_to_integer():
    assert compound_interest(100, 0.0123, 1) == pytest.approx(101.23)


@pytest.mark.parametrize("args", [(-1, 0.05, 1), (100, -0.05, 1), (100, 0.05, -1)])
def test_negative_values_rejected(args):
    with pytest.raises(ValueError):
        compound_interest(*args)


def test_periods_must_be_positive():
    with pytest.raises(ValueError):
        compound_interest(100, 0.05, 1, periods=0)
