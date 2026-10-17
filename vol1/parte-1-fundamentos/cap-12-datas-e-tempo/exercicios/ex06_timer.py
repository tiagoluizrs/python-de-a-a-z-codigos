"""Exercício 6: medir duração com perf_counter em um context manager."""


class Timer:
    """Mede quanto tempo um bloco ``with`` leva.

    >>> with Timer() as t:
    ...     total = sum(range(1000))
    >>> t.elapsed >= 0
    True

    Requisitos:
    - Use ``time.perf_counter_ns()`` (inteiro, sem erro de float).
    - ``elapsed_ns`` (int) e ``elapsed`` (float, em segundos) ficam
      disponíveis DEPOIS do bloco (e valem 0 antes dele terminar).
    - Se o bloco levantar exceção, o tempo ainda é registrado e a
      exceção NÃO pode ser engolida (``__exit__`` devolve falso).
    - ``__enter__`` devolve o próprio objeto.

    Um context manager é uma classe com ``__enter__`` (chamado ao
    entrar no ``with``) e ``__exit__(exc_type, exc, traceback)`` (ao
    sair). O assunto completo está no Capítulo 8 do Volume 2.
    """

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, traceback):
        raise NotImplementedError
