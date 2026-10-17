"""Exercício 4: um cache LRU em cima da ordem do dict."""


class LRUCache:
    """Cache de tamanho fixo que descarta o item MENOS recentemente usado.

    * ``LRUCache(capacity)``;
    * ``get(key, default=None)``: devolve o valor e marca a chave como a
      mais recente; se não existir, devolve ``default``;
    * ``put(key, value)``: grava (ou atualiza) e marca como a mais
      recente; se passar da capacidade, remove a menos recente;
    * ``__len__`` e ``keys()`` (da menos para a mais recente).

    Dica: ``dict`` preserva a ordem de inserção; ``pop`` e reinserção
    movem uma chave para o fim. ``collections.OrderedDict`` também serve.
    """

    def __init__(self, capacity: int):
        raise NotImplementedError
