"""Exercício 3: medindo colisões pelo número de chamadas a __eq__."""


def count_eq_calls(n: int, hash_fn) -> int:
    """Insira ``n`` chaves em um dict e devolva quantas vezes ``__eq__``
    foi chamado.

    Cada chave é um objeto que guarda um inteiro ``i`` (de 0 a n-1), tem
    ``__hash__`` igual a ``hash_fn(i)`` e um ``__eq__`` que conta as
    chamadas (e compara os valores ``i``).

    O dict só chama ``__eq__`` entre chaves com o MESMO hash completo.
    Resultados esperados: ``hash_fn = lambda i: i`` dá 0; hash constante
    com n = 100 dá 4950; ``lambda i: i % 10`` com n = 100 dá 450.
    """
    raise NotImplementedError
