"""Exercício 1: um cache LRU com OrderedDict."""


class LRUCache:
    """Cache de capacidade fixa com despejo do MENOS recentemente usado.

    * ``LRUCache(capacity)`` (``capacity < 1`` levanta ``ValueError``);
    * ``get(key, default=None)``: devolve o valor e marca a chave como a mais
      recente; ausente devolve ``default``;
    * ``put(key, value)``: grava (atualizar também marca como mais recente);
      ao exceder a capacidade, remove a menos recente;
    * ``len(cache)``, ``key in cache`` (``in`` NÃO altera a recência) e
      ``keys()`` devolvendo a lista do MENOS para o MAIS recente.
    """

    def __init__(self, capacity):
        raise NotImplementedError
