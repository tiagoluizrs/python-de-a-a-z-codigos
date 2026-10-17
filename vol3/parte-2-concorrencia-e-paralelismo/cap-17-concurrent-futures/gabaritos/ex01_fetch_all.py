"""Gabarito do exercício 1."""
import concurrent.futures as cf
from dataclasses import dataclass


@dataclass
class Outcome:
    index: int
    value: object = None
    error: Exception | None = None

    @property
    def ok(self):
        return self.error is None


def fetch_all(func, items, workers=4):
    if workers < 1:
        raise ValueError("workers >= 1")
    items = list(items)
    if not items:
        return []
    outcomes = [None] * len(items)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(func, item): index for index, item in enumerate(items)}
        for future in cf.as_completed(futures):
            index = futures[future]
            error = future.exception()
            if error is None:
                outcomes[index] = Outcome(index, value=future.result())
            else:
                outcomes[index] = Outcome(index, error=error)
    return outcomes
