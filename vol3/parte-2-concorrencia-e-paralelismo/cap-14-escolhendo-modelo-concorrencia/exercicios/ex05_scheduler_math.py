"""Exercício 5: dimensionar um pool para E/S (lei de Little)."""


def pool_size(requests_per_second, seconds_per_request, utilization=1.0):
    """Lei de Little: trabalhadores = chegada × tempo de serviço (``L = λW``).
    ``ceil(requests_per_second * seconds_per_request / utilization)``, no mínimo 1.
    ``utilization`` em ``(0, 1]``; fora disso, ``ValueError``."""
    raise NotImplementedError


def throughput(workers, seconds_per_request):
    """Requisições por segundo que ``workers`` trabalhadores sustentam:
    ``workers / seconds_per_request``."""
    raise NotImplementedError


def total_time(items, workers, seconds_per_item):
    """Tempo total para ``items`` tarefas iguais em ``workers`` trabalhadores:
    ``ceil(items / workers) * seconds_per_item`` (as rodadas completas contam)."""
    raise NotImplementedError
