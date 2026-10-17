"""Exercício 3: escreva testes para ``compound_interest``.

``compound_interest(principal, rate, years, periods=1)``:
``principal * (1 + rate/periods) ** (periods*years)``; ``rate`` é fração
(0.05 = 5%); negativos e ``periods < 1`` levantam ``ValueError``.

Use ``pytest.approx`` e ``@pytest.mark.parametrize``. Os 7 mutantes erram o
percentual, ignoram períodos, contam um ano a mais, arredondam, ou deixam de
validar. Seus testes têm de matá-los todos e passar no correto.
"""
import pytest
from interest_impl import compound_interest


def test_exemplo():
    assert compound_interest(1000, 0.05, 10) == pytest.approx(1628.894627, rel=1e-6)

# escreva os demais testes abaixo
