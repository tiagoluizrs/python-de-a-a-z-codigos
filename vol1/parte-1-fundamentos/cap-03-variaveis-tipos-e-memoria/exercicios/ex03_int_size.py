"""Exercício 3: prevendo o tamanho de um int no CPython (64 bits)."""


def predicted_int_size(n: int) -> int:
    """Preveja ``sys.getsizeof(n)`` SEM chamar ``getsizeof``.

    O CPython guarda o valor absoluto em 'dígitos' de 30 bits (4 bytes cada),
    após um cabeçalho de 24 bytes. Zero ocupa o mesmo que 1 dígito.
    """
    raise NotImplementedError
