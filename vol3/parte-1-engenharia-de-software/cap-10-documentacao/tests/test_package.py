"""Os testes do pacote shapes (os doctests rodam com --doctest-modules)."""
import pytest

from shapes import Circle, Rectangle, largest, total_area


def test_total_area():
    assert total_area([Rectangle(1, 2), Rectangle(3, 4)]) == 14 and total_area([]) == 0


def test_largest_and_errors():
    assert largest([Rectangle(1, 1), Rectangle(2, 2)]).width == 2
    with pytest.raises(ValueError):
        largest([])
    with pytest.raises(ValueError):
        Circle(-1)
