"""Exercício 2: o que o compilador faz com as constantes."""


def constants_of(source):
    """Compila ``source`` (texto) e devolve a lista ORDENADA e sem repetição
    (``sorted``, por ``repr``) das constantes ``int``, ``float`` e ``str`` do
    código, inclusive as dos objetos de código aninhados (funções, lambdas).
    ``bool`` e ``None`` não entram."""
    raise NotImplementedError


def is_folded(expression):
    """``True`` se o compilador reduz ``expression`` (uma expressão, em
    texto) a uma constante, isto é, o código gerado NÃO contém instruções
    ``BINARY_OP`` nem ``CALL``. ``is_folded("2 * 3 + 1")`` -> ``True``;
    ``is_folded("x + 1")`` -> ``False``."""
    raise NotImplementedError
