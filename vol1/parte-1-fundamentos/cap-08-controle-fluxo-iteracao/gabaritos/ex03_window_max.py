"""Gabarito do exercício 3 (versão O(n) com deque monotônico)."""
from collections import deque


def window_max(values: list[int], k: int) -> list[int]:
    if k < 1:
        raise ValueError("k must be >= 1")
    result = []
    candidates = deque()   # índices; valores correspondentes decrescentes
    for index, value in enumerate(values):
        # quem é menor ou igual ao novo valor nunca mais será o máximo
        while candidates and values[candidates[-1]] <= value:
            candidates.pop()
        candidates.append(index)
        # o índice da frente saiu da janela?
        if candidates[0] <= index - k:
            candidates.popleft()
        # a janela só está completa a partir do índice k - 1
        if index >= k - 1:
            result.append(values[candidates[0]])
    return result
