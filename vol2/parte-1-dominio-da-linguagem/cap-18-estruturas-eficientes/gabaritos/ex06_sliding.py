"""Gabarito do exercício 6."""
from collections import deque


def moving_average(values, size):
    if size < 1:
        raise ValueError("size deve ser >= 1")
    window = deque()
    total = 0
    for value in values:
        window.append(value)
        total += value
        if len(window) > size:
            total -= window.popleft()
        if len(window) == size:
            yield total / size


def max_sliding_window(numbers, size):
    if size < 1:
        raise ValueError("size deve ser >= 1")
    result = []
    indexes = deque()                              # índices; valores em ordem decrescente
    for i, value in enumerate(numbers):
        while indexes and numbers[indexes[-1]] <= value:
            indexes.pop()
        indexes.append(i)
        if indexes[0] <= i - size:
            indexes.popleft()
        if i >= size - 1:
            result.append(numbers[indexes[0]])
    return result
