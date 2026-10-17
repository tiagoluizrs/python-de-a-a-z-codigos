"""Exercício 1: as leis do ganho paralelo."""


def amdahl_speedup(parallel_fraction, workers):
    """Lei de Amdahl: ``1 / ((1 - p) + p / n)``. ``p`` em ``[0, 1]`` e ``n >= 1``
    (``float``/``int``); fora disso, ``ValueError``."""
    raise NotImplementedError


def efficiency(parallel_fraction, workers):
    """Eficiência: ``speedup / workers`` (fração do ideal aproveitada)."""
    raise NotImplementedError


def max_speedup(parallel_fraction):
    """Limite com infinitos trabalhadores: ``1 / (1 - p)``; ``float("inf")`` se ``p == 1``."""
    raise NotImplementedError


def gustafson_speedup(parallel_fraction, workers):
    """Lei de Gustafson (problema que cresce com os trabalhadores):
    ``(1 - p) + p * n``."""
    raise NotImplementedError


def best_worker_count(parallel_fraction, minimum_efficiency=0.5, limit=64):
    """O MAIOR número de trabalhadores ``n`` (``1 <= n <= limit``) em que a
    eficiência ainda é ``>= minimum_efficiency``. Para ``p = 0`` devolve ``1``."""
    raise NotImplementedError
