"""Exercício 4: run-length encoding com itertools.groupby."""


def rle_encode(text: str) -> list[tuple[str, int]]:
    """Comprima ``text`` em pares ``(caractere, repetições)``.

    ``rle_encode("aaabcc") == [("a", 3), ("b", 1), ("c", 2)]``.
    Texto vazio devolve lista vazia. Use ``itertools.groupby``
    (lembre: ele agrupa vizinhos iguais, então NÃO ordene).
    """
    raise NotImplementedError


def rle_decode(pairs: list[tuple[str, int]]) -> str:
    """Operação inversa: ``rle_decode([("a", 3), ("b", 1)]) == "aaab"``."""
    raise NotImplementedError
