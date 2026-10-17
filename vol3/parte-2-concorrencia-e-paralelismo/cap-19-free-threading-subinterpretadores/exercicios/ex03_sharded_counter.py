"""Exercício 3: reduzir a disputa por estado compartilhado."""


class ShardedCounter:
    """Contador para muitas threads com POUCA disputa.

    * ``ShardedCounter(shards=8)``: ``shards < 1`` levanta ``ValueError``;
    * mantém ``shards`` contadores independentes, cada um com SUA trava; a thread
      que chama ``add`` usa o fragmento ``threading.get_ident() % shards``;
    * ``add(n=1)``: soma ``n`` ao fragmento da thread atual;
    * ``total()``: soma de todos os fragmentos (consistente: tome as travas em
      ordem, uma de cada vez, e some);
    * ``reset()``: zera todos e devolve o total anterior."""

    def __init__(self, shards=8):
        raise NotImplementedError
