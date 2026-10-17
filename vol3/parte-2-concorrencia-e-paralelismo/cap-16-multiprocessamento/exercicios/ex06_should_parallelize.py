"""Exercício 6: vale a pena paralelizar? (a conta do Capítulo 14 com custos reais)"""


def estimate_parallel_time(total_work, tasks, workers, startup=0.12, per_task_overhead=0.0001):
    """Estimativa do tempo com um ``Pool``: ``startup`` (criar o pool) + o trabalho
    em RODADAS completas (``ceil(tasks / workers)`` rodadas de
    ``total_work / tasks`` segundos cada) + ``tasks * per_task_overhead``
    (cópia/mensagens). ``tasks`` e ``workers`` devem ser >= 1 (``ValueError``)."""
    raise NotImplementedError


def should_parallelize(total_work, tasks, workers, **costs):
    """``True`` se a estimativa paralela for MENOR que ``total_work`` (o tempo
    sequencial); ``False`` caso contrário."""
    raise NotImplementedError
