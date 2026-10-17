"""Exercício 5: ferramentas com reduce e operator."""


def merge_dicts(*dicts):
    """Mescla os dicionários, da esquerda para a direita, SEM alterar nenhum;
    chaves repetidas ficam com o último valor. Use ``functools.reduce`` e o
    operador ``|``. Sem argumentos, devolve ``{}``."""
    raise NotImplementedError


def deep_get(data, path, default=None):
    """``deep_get({"a": [{"b": 5}]}, ["a", 0, "b"])`` -> ``5``. Percorre
    ``path`` com ``functools.reduce`` e ``operator.getitem``. Se algum passo
    falhar (``KeyError``, ``IndexError`` ou ``TypeError``), devolve ``default``."""
    raise NotImplementedError


def product(numbers):
    """Produto dos números (``1`` para vazio). Use ``reduce`` e ``operator.mul``."""
    raise NotImplementedError


def group_by(items, key):
    """Agrupa ``items`` pela função ``key``, devolvendo ``dict[chave, list]``
    com as chaves na ordem da primeira aparição e os itens na ordem original.
    Use ``reduce`` (com um dict inicial) OU ``itertools.groupby`` sobre a lista
    ORDENADA, como preferir."""
    raise NotImplementedError
