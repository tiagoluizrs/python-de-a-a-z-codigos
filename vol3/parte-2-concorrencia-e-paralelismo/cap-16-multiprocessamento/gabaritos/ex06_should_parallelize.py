"""Gabarito do exercício 6."""
import math


def estimate_parallel_time(total_work, tasks, workers, startup=0.12, per_task_overhead=0.0001):
    if tasks < 1 or workers < 1:
        raise ValueError("tasks e workers >= 1")
    rounds = math.ceil(tasks / workers)
    return startup + rounds * (total_work / tasks) + tasks * per_task_overhead


def should_parallelize(total_work, tasks, workers, **costs):
    return estimate_parallel_time(total_work, tasks, workers, **costs) < total_work
