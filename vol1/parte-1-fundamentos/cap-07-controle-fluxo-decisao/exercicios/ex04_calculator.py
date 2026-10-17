"""Exercício 4: calculadora sobre uma mini AST em tuplas."""


def evaluate(node):
    """Avalie uma expressão representada por tuplas.

    - número (``int`` ou ``float``) -> ele mesmo
    - ``("+", a, b)``, ``("-", a, b)``, ``("*", a, b)``, ``("/", a, b)``
    - ``("neg", a)`` -> ``-a``
    - ``("sum", [e1, e2, ...])`` -> soma de todas (lista de nós)
    - operador desconhecido ou nó mal formado -> ``ValueError``
    - divisão por zero deixa ``ZeroDivisionError`` subir.

    Exemplo: ``evaluate(("+", 2, ("*", 3, 4))) == 14``.
    Dica: ``bool`` é subclasse de ``int``; rejeite ``True``/``False``
    (``case bool(): raise ValueError``) antes de ``int()``.
    """
    raise NotImplementedError
