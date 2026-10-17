"""Fixtures compartilhadas pelos testes desta pasta (descobertas automaticamente)."""
import pytest

from pricing import Cart

CALLS = []


@pytest.fixture
def cart():
    """Um carrinho novo para cada teste (escopo de função, o padrão)."""
    return Cart()


@pytest.fixture
def filled_cart(cart):
    """Fixtures podem depender de outras fixtures."""
    cart.add("A1", 10.0, 2)
    cart.add("B2", 5.5)
    return cart
