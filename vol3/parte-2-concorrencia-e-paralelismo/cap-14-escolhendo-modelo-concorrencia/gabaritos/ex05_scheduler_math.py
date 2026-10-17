"""Gabarito do exercício 5."""
import math


def pool_size(requests_per_second, seconds_per_request, utilization=1.0):
    if not 0 < utilization <= 1:
        raise ValueError("utilization em (0, 1]")
    return max(1, math.ceil(requests_per_second * seconds_per_request / utilization))


def throughput(workers, seconds_per_request):
    return workers / seconds_per_request


def total_time(items, workers, seconds_per_item):
    return math.ceil(items / workers) * seconds_per_item
