"""Gabarito do exercício 2."""
import math
import multiprocessing as mp


def parallel_map(func, items, processes=2, chunksize=None):
    if processes < 1:
        raise ValueError("processes >= 1")
    items = list(items)
    if not items:
        return []
    if chunksize is None:
        chunksize = max(1, math.ceil(len(items) / (processes * 4)))
    with mp.Pool(processes) as pool:
        return pool.map(func, items, chunksize=chunksize)
