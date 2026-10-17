"""Exercício 1: ferramentas de medição."""
import time


class Timer:
    """Gerenciador de contexto que mede a duração do bloco.

    ``with Timer() as t: ...``; depois do bloco, ``t.elapsed`` tem os segundos
    (``float``) e ``t.elapsed_ns`` os nanossegundos (``int``). Use o relógio
    recebido em ``clock_ns`` (padrão ``time.perf_counter_ns``; o teste injeta um
    falso). Dentro do ``with``, ``t.elapsed`` já mostra o tempo decorrido até
    ali. Se o bloco levantar exceção, o tempo ainda é registrado e a exceção
    propaga."""

    def __init__(self, clock_ns=time.perf_counter_ns):
        raise NotImplementedError


def benchmark(func, *args, repeat=5, number=10, clock_ns=time.perf_counter_ns, **kwargs):
    """Executa ``func(*args, **kwargs)`` ``number`` vezes por rodada, em
    ``repeat`` rodadas, e devolve um dict com os tempos POR CHAMADA (segundos):
    ``{"min", "median", "mean", "stdev", "runs"}`` onde ``runs`` é a lista dos
    ``repeat`` tempos por chamada. ``stdev`` é ``0.0`` se ``repeat == 1``.
    ``repeat`` ou ``number`` menores que 1 levantam ``ValueError``."""
    raise NotImplementedError
