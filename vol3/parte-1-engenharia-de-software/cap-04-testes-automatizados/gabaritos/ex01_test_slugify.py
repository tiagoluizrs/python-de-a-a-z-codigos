"""Gabarito do exercício 1."""
import pytest
from slugify_impl import slugify


@pytest.mark.parametrize("text, expected", [
    ("Olá Mundo", "ola-mundo"),
    ("Ação e Reação", "acao-e-reacao"),
    ("MAIÚSCULAS", "maiusculas"),
    ("a   b", "a-b"),
    ("a - b", "a-b"),
    ("--oi--", "oi"),
    ("  espaços  ", "espacos"),
    ("Python 3.15", "python-3-15"),
    ("abc123", "abc123"),
    ("", ""),
    ("???", ""),
    ("já-está", "ja-esta"),
])
def test_slugify(text, expected):
    assert slugify(text) == expected
