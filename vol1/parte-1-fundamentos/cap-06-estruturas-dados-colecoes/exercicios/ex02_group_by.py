"""Exercício 2: agrupar itens por chave."""
from collections.abc import Callable, Iterable


def group_by(items: Iterable, key: Callable) -> dict:
    """Agrupe ``items`` em um dict ``{key(item): [itens...]}``.

    A ordem dos grupos segue a primeira aparição da chave e a ordem
    dentro de cada grupo segue a de entrada.

    ``group_by(["apple", "avocado", "fig"], len)``
    devolve ``{5: ["apple"], 7: ["avocado"], 3: ["fig"]}``.

    Não use ``collections.defaultdict`` (é assunto do Capítulo 18 do Volume 2):
    use ``setdefault`` ou ``get``.
    """
    raise NotImplementedError
