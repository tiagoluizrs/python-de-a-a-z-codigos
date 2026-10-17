"""Exercício 4: aritmética de dinheiro com erro de domínio."""
from decimal import Decimal


class CurrencyMismatch(ValueError):
    """Somar ou comparar moedas diferentes é um erro de DOMÍNIO."""


class Money:
    """Dinheiro: ``Money(Decimal("19.90"), "BRL")``.

    * ``+`` e ``-`` entre ``Money`` da MESMA moeda; moedas diferentes
      levantam ``CurrencyMismatch`` (e NÃO ``TypeError``);
    * ``Money + 0`` e ``sum(lista_de_money)`` funcionam (``0`` é aceito);
    * ``*`` por ``int`` ou ``Decimal`` (dos dois lados);
    * ``/`` por ``int``/``Decimal`` devolve ``Money``; ``Money / Money`` (mesma
      moeda) devolve a razão como ``Decimal``;
    * ``-m``, ``abs(m)``, ``bool(m)`` (falso se zero);
    * ordenação ``<``, ``<=``, ``>``, ``>=`` e ``==`` na mesma moeda
      (``==`` com moedas diferentes é simplesmente ``False``);
    * ``hash`` coerente e ``repr`` ``Money(Decimal('19.90'), 'BRL')``;
    * outros tipos: ``NotImplemented``.
    """

    def __init__(self, amount, currency):
        raise NotImplementedError
