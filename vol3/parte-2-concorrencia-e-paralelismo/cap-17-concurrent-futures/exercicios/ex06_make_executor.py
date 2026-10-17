"""Exercício 6: escolher o executor pelo nome e dividir em lotes."""


def make_executor(kind, workers=2):
    """Devolve um executor novo (o chamador usa ``with``):
    ``"thread"`` -> ``ThreadPoolExecutor``, ``"process"`` -> ``ProcessPoolExecutor``,
    ``"interpreter"`` -> ``InterpreterPoolExecutor``. Outro ``kind`` levanta
    ``ValueError``; ``workers < 1`` também."""
    raise NotImplementedError


def batched_map(executor, func, items, batch_size):
    """Divide ``items`` em lotes de ``batch_size`` (o último pode ser menor) e executa
    UMA tarefa por lote com ``tasks.apply_batch(func, lote)`` (módulo ``tasks``,
    importável por processos). Devolve os resultados achatados, NA ORDEM.
    ``func`` precisa ser picklável para o executor de processos;
    ``batch_size < 1`` levanta ``ValueError``; ``items`` vazio devolve ``[]``."""
    raise NotImplementedError
