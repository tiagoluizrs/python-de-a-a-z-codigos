"""Exercício 4: prevendo o tamanho de um str no CPython."""


def predicted_str_size(text: str) -> int:
    """Preveja ``sys.getsizeof(text)`` SEM chamar ``getsizeof``.

    Regras (CPython 3.15, 64 bits, textos com 2+ caracteres):
    - só ASCII           : 40 + n + 1
    - maior ponto < 256  : 56 + n + 1
    - maior ponto < 65536: 56 + 2n + 2
    - demais             : 56 + 4n + 4
    """
    raise NotImplementedError
