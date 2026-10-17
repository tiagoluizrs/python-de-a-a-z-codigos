"""Gabarito do exercício 1."""
import math


def split_chunks(items, n):
    if n < 1:
        raise ValueError("n >= 1")
    items = list(items)
    base, extra = divmod(len(items), n)
    chunks, start = [], 0
    for index in range(n):
        size = base + (1 if index < extra else 0)
        chunks.append(items[start:start + size])
        start += size
    return chunks


def chunk_size(total, workers, factor=4):
    if workers < 1 or factor < 1:
        raise ValueError("workers e factor >= 1")
    return max(1, math.ceil(total / (workers * factor)))
