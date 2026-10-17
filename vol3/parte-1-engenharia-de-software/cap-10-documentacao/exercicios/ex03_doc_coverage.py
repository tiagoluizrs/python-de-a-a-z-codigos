"""Exercício 3: cobertura de docstrings."""


def docstring_coverage(source):
    """Analisa ``source`` (texto Python) com ``ast`` e devolve
    ``(documentados, total, faltando)``.

    Conta como item documentável: o MÓDULO (nome ``"<module>"``), cada classe e
    cada função/método PÚBLICOS (nome sem ``_`` inicial; ``__init__`` e demais
    métodos mágicos NÃO contam), em qualquer nível EXCETO funções definidas
    dentro de outras funções. Um item é documentado se tem docstring. ``faltando``
    é a lista ORDENADA dos nomes qualificados sem docstring (``"Classe.metodo"``,
    ``"<module>"``)."""
    raise NotImplementedError


def percentage(documented, total):
    """Percentual (``float`` com 1 casa) ou ``100.0`` se ``total == 0``."""
    raise NotImplementedError
