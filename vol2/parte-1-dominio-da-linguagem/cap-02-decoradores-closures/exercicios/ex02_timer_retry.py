"""Exercício 2: um timer e um retry com backoff."""
import time


def timer(func):
    """Decorador que mede cada chamada com ``time.perf_counter``.

    - guarde a duração (em segundos) da última chamada no atributo
      ``wrapper.last_elapsed`` (comece em ``None``);
    - registre a duração mesmo se a função levantar exceção
      (a exceção deve continuar subindo);
    - preserve ``__name__`` e ``__doc__`` com ``functools.wraps``.
    """
    raise NotImplementedError


def retry(times, exceptions=(Exception,), delay=0.1, backoff=2.0,
          sleep=time.sleep):
    """Fábrica de decoradores: tenta a função até ``times`` vezes.

    - só repete se a exceção for de um tipo em ``exceptions``;
      outras exceções sobem imediatamente;
    - entre tentativas, chame ``sleep(espera)``: a primeira espera é
      ``delay`` e cada uma seguinte é multiplicada por ``backoff``;
    - não durma depois da última tentativa: levante a última exceção;
    - preserve os metadados com ``functools.wraps``.

    Com times=4, delay=1, backoff=2 as esperas são 1, 2 e 4.
    ``sleep`` é injetável para que o teste não precise esperar.
    """
    raise NotImplementedError
