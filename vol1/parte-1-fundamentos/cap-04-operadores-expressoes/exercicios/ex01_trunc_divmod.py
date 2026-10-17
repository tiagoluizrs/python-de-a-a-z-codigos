"""Exercício 1: divisão 'à moda do C' (truncando em direção a zero)."""


def trunc_divmod(a: int, b: int) -> tuple[int, int]:
    """Devolva ``(quociente, resto)`` como o C faz: o quociente é TRUNCADO
    em direção a zero e o resto tem o sinal do DIVIDENDO.

    Exemplos: ``trunc_divmod(-7, 2) == (-3, -1)`` (o Python daria (-4, 1)).
    Proibido usar ``math.trunc`` ou ``int()`` sobre uma divisão com ``/``
    (floats perdem precisão em inteiros grandes).
    Lance ``ZeroDivisionError`` se ``b == 0``.
    """
    raise NotImplementedError
