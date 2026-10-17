"""Exercício 2: ordenação de versões."""


class Version:
    """Versão semântica ``major.minor.patch`` (com 1 a 3 partes).

    * ``Version("1.10.2")``; ``Version("2")`` equivale a ``2.0.0``;
    * ``repr`` no formato ``Version('1.10.2')`` (texto original);
    * ``==``, ``<``, ``<=``, ``>``, ``>=`` entre versões (use
      ``functools.total_ordering`` ou escreva todos);
    * comparar com ``str`` também funciona: ``Version("1.2") < "1.10"`` é
      verdadeiro (converta o texto); com outros tipos, ``NotImplemented``;
    * ``hash`` coerente: ``Version("1.0") == Version("1.0.0")`` com hashes
      iguais;
    * ``sorted`` e ``max`` sobre listas de ``Version`` funcionam.
    """

    def __init__(self, text):
        raise NotImplementedError
