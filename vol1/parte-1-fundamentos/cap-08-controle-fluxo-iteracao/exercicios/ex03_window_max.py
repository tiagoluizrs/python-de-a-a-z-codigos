"""Exercício 3: máximo de cada janela deslizante."""


def window_max(values: list[int], k: int) -> list[int]:
    """Devolva o máximo de cada janela de ``k`` itens consecutivos.

    Exemplo: ``window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)``
    devolve ``[3, 3, 5, 5, 6, 7]``.

    Se ``k > len(values)`` ou ``values`` estiver vazia, devolva ``[]``.
    Lance ``ValueError`` se ``k < 1``.

    Versão simples: ``max(values[i:i + k])`` por janela, O(n * k).
    Desafio: O(n) com ``collections.deque`` guardando ÍNDICES cujos
    valores estão em ordem decrescente (descarte do fim os menores
    que o novo valor e do início o índice que saiu da janela).
    """
    raise NotImplementedError
