"""Exercício 1: reimplementar lru_cache."""


def memoize(maxsize=128):
    """Decorador com parâmetro: ``@memoize(maxsize=2)`` (``None`` = sem limite).

    * a chave usa ``args`` e ``tuple(sorted(kwargs.items()))``; argumentos
      não hasheáveis levantam ``TypeError`` (naturalmente);
    * política **LRU**: ao exceder ``maxsize``, descarta o menos recentemente
      USADO (um acerto conta como uso); use ``collections.OrderedDict``;
    * a função decorada ganha ``cache_info()`` (devolve uma tupla nomeada
      ``(hits, misses, maxsize, currsize)``) e ``cache_clear()``;
    * preserve ``__name__`` e ``__doc__`` com ``functools.wraps``.
    """
    raise NotImplementedError
