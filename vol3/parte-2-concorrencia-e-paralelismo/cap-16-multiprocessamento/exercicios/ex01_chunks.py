"""Exercício 1: dividir o trabalho em pedaços."""


def split_chunks(items, n):
    """Divide ``items`` em EXATAMENTE ``n`` pedaços consecutivos (listas), mantendo a
    ordem, com tamanhos que diferem em no máximo 1 (os maiores primeiro).
    ``split_chunks(range(7), 3) -> [[0, 1, 2], [3, 4], [5, 6]]``.
    Se ``n`` for maior que os itens, sobram pedaços vazios; ``n < 1`` levanta ``ValueError``."""
    raise NotImplementedError


def chunk_size(total, workers, factor=4):
    """Tamanho de ``chunksize`` sugerido: ``ceil(total / (workers * factor))``, no
    mínimo 1 (como o ``Pool.map`` faz). ``total == 0`` devolve 1;
    ``workers < 1`` ou ``factor < 1`` levantam ``ValueError``."""
    raise NotImplementedError
