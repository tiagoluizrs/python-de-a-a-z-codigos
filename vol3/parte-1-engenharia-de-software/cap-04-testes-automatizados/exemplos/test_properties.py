"""Testes baseados em propriedades (Hypothesis): descreva o INVARIANTE, não os exemplos."""
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from pricing import apply_discount, parse_price


@given(price=st.floats(min_value=0, max_value=1e6), percent=st.floats(min_value=0, max_value=100))
def test_discount_never_increases_and_never_negative(price, percent):
    result = apply_discount(price, percent)
    assert 0 <= result <= round(price, 2) + 0.01


@given(st.integers(min_value=0, max_value=10**9), st.integers(min_value=0, max_value=99))
def test_parse_price_roundtrip(units, cents):
    text = f"R$ {units:,}".replace(",", ".") + f",{cents:02d}"
    assert parse_price(text) == Decimal(units) + Decimal(cents) / 100


@settings(max_examples=50)
@given(st.lists(st.integers()))
def test_sorting_is_idempotent_and_keeps_length(xs):
    once = sorted(xs)
    assert sorted(once) == once and len(once) == len(xs)
