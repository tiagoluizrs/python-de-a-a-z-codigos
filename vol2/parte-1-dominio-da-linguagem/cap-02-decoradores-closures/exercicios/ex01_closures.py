"""Exercício 1: closures, estado privado e late binding."""


def make_multipliers(n):
    """Devolva uma lista de ``n`` funções; a de índice ``i`` multiplica
    seu argumento por ``i``.

    >>> [f(10) for f in make_multipliers(3)]
    [0, 10, 20]

    Um laço ingênuo com ``lambda x: x * i`` devolveria [20, 20, 20].
    Corrija o late binding (argumento padrão, partial ou fábrica).
    """
    raise NotImplementedError


def make_accumulator(start=0):
    """Devolva uma tupla ``(add, total, reset)`` de três funções que
    compartilham UM estado privado (use ``nonlocal``):

    - ``add(x)``: soma x ao total e devolve o novo total;
    - ``total()``: devolve o total atual;
    - ``reset()``: volta o total para ``start`` e devolve ``None``.

    O total não pode ser um atributo nem uma variável global.
    """
    raise NotImplementedError
