"""Exercício 5: reimplementando batched e pairwise."""


def my_batched(iterable, n: int, *, strict: bool = False):
    """Agrupe ``iterable`` em tuplas de até ``n`` itens.

    Deve se comportar como ``itertools.batched``:
    ``list(my_batched("ABCDEFG", 3))`` é
    ``[("A","B","C"), ("D","E","F"), ("G",)]``.
    Com ``strict=True``, um último bloco incompleto lança
    ``ValueError``. Lance ``ValueError`` se ``n < 1``.

    Deve funcionar com QUALQUER iterável (inclusive iteradores, que
    não aceitam fatias): use ``iter()`` e ``next()``, ou
    ``itertools.islice``. Pode devolver uma lista ou ser um
    generator (com ``yield``, tema do Capítulo 4 do Volume 2): os testes
    usam ``list(...)``.
    """
    raise NotImplementedError


def my_pairwise(iterable):
    """Pares sobrepostos: ``[1, 2, 3]`` -> ``(1, 2), (2, 3)``.

    Menos de dois itens: nenhum par. Deve funcionar com iteradores.
    Dica: guarde o item anterior numa variável.
    """
    raise NotImplementedError
