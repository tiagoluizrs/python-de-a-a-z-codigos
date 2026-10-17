"""Exercício 5: calculadora que não executa código."""
import ast


def safe_eval(expression, *, max_length=100, max_exponent=100):
    """Calcula uma expressão aritmética usando ``ast`` (NUNCA ``eval``).

    Permitido: números ``int`` e ``float`` (não ``bool``), parênteses, ``+``
    ``-`` ``*`` ``/`` ``//`` ``%`` ``**`` e ``+``/``-`` unários.

    Levante ``ValueError`` para: texto maior que ``max_length``; sintaxe
    inválida; qualquer outro nó (nomes, chamadas, atributos, textos,
    comparações, listas, ``lambda``...); expoente MAIOR que ``max_exponent``
    (em valor absoluto) em ``**``. Divisão por zero levanta
    ``ZeroDivisionError`` normalmente."""
    raise NotImplementedError
