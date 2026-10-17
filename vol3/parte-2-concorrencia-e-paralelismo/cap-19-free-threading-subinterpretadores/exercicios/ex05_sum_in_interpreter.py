"""Exercício 5: conversar com um subinterpretador por filas."""


def sum_in_interpreter(numbers):
    """Crie um subinterpretador (``concurrent.interpreters.create()``) e duas filas
    (``create_queue()``): ``jobs`` e ``results``. Injete as duas no subinterpretador
    com ``prepare_main(jobs=jobs, results=results)`` e peça (``exec``) que ele leia
    de ``jobs`` até receber ``None``, somando os números, e então ponha o total em
    ``results``.

    O principal envia cada número em ``jobs`` e depois ``None`` e lê o total.
    Devolva o total (``0`` para lista vazia). O subinterpretador deve ser
    FECHADO (``close``) sempre, inclusive se algo falhar."""
    raise NotImplementedError
