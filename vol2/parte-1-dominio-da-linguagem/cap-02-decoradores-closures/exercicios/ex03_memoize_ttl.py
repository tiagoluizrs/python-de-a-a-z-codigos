"""Exercício 3: memoize com tempo de vida (TTL)."""
import time


def memoize(ttl, clock=time.monotonic):
    """Fábrica de decoradores: guarda resultados por ``ttl`` segundos.

    - a chave é formada por argumentos posicionais E nomeados
      (``f(1, b=2)`` e ``f(1, b=2)`` são a mesma chamada; a ordem dos
      nomeados não importa);
    - uma entrada vale enquanto ``clock() - criada_em < ttl``;
    - exceções NÃO são guardadas;
    - ``wrapper.cache_clear()`` esvazia o cache;
    - ``wrapper.cache_size()`` devolve quantas entradas existem
      (inclusive as expiradas que ainda não foram removidas);
    - preserve os metadados com ``functools.wraps``.

    ``clock`` é injetável para o teste controlar o tempo.
    """
    raise NotImplementedError
