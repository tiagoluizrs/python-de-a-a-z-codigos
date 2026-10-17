"""Gabarito do exercício 6."""
import concurrent.futures as cf

import tasks


def make_executor(kind, workers=2):
    if workers < 1:
        raise ValueError("workers >= 1")
    classes = {"thread": cf.ThreadPoolExecutor, "process": cf.ProcessPoolExecutor, "interpreter": cf.InterpreterPoolExecutor}
    if kind not in classes:
        raise ValueError(f"kind desconhecido: {kind!r}")
    return classes[kind](max_workers=workers)


def batched_map(executor, func, items, batch_size):
    if batch_size < 1:
        raise ValueError("batch_size >= 1")
    items = list(items)
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    if not batches:
        return []
    results = executor.map(tasks.apply_batch, [func] * len(batches), batches)
    return [value for batch in results for value in batch]
