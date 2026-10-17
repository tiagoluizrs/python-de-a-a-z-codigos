"""Gabarito do exercício 4."""
import concurrent.futures as cf

import tasks


def split(data, parts):
    if parts < 1:
        raise ValueError("parts >= 1")
    data = list(data)
    base, extra = divmod(len(data), parts)
    chunks, start = [], 0
    for index in range(parts):
        size = base + (1 if index < extra else 0)
        chunks.append(data[start:start + size])
        start += size
    return chunks


def sum_squares_parallel(data, workers=2, kind="thread"):
    classes = {"thread": cf.ThreadPoolExecutor, "process": cf.ProcessPoolExecutor, "interpreter": cf.InterpreterPoolExecutor}
    if kind not in classes:
        raise ValueError(f"kind desconhecido: {kind!r}")
    data = list(data)
    if not data:
        return 0
    with classes[kind](max_workers=workers) as pool:
        return sum(pool.map(tasks.sum_squares, split(data, workers)))
