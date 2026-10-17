"""Exercício 1: as três vozes de um objeto (repr, str e format)."""


class Money:
    """Dinheiro em centavos.

    * ``Money(1990)`` e ``Money(1990, "USD")`` (moeda padrão ``"BRL"``);
    * ``repr`` no formato ``Money(1990, 'BRL')``;
    * ``str`` no formato ``R$ 19,90`` para BRL e ``USD 19.90`` para as demais
      moedas;
    * ``format(m, "")`` igual a ``str(m)``; ``format(m, "plain")`` devolve
      ``"19.90"``; ``format(m, "code")`` devolve ``"BRL 19.90"``;
      qualquer outro ``spec`` levanta ``ValueError``;
    * ``bool(Money(0))`` é ``False``;
    * ``==`` compara centavos E moeda (``NotImplemented`` para outros tipos) e
      ``hash`` é coerente com ``==``.
    """

    def __init__(self, cents, currency="BRL"):
        raise NotImplementedError
