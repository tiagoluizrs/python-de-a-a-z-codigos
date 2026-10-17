"""Exercício 5: um repositório sobre uma coleção MongoDB."""


class ProductStore:
    """``ProductStore(collection)``, ``collection`` do pymongo.

    * ``ensure_indexes()``: índice ÚNICO em ``sku`` (idempotente);
    * ``add(sku, name, price, stock=0)``: ``price`` é ``decimal.Decimal`` e vai como ``Decimal128``;
      devolve o documento criado (com ``_id``); ``sku`` repetido levanta ``ValueError``
      (``DuplicateKeyError``); ``stock < 0`` levanta ``ValueError`` antes de tocar no banco;
    * ``get(sku)`` -> documento com ``price`` já como ``Decimal`` ou ``None``;
    * ``remove_stock(sku, quantity)``: baixa o estoque de forma ATÔMICA em UMA operação
      (``find_one_and_update`` com filtro ``stock >= quantity`` e ``$inc``), devolve o estoque restante;
      sem estoque suficiente levanta ``ValueError``, SKU inexistente levanta ``KeyError``;
      ``quantity < 1`` levanta ``ValueError``; 8 threads concorrentes nunca vendem mais que o estoque;
    * ``page(after_id=None, limit=3)`` -> ``(documentos, proximo_id)`` por ``_id`` crescente (paginação por
      chave: ``_id > after_id``); ``proximo_id`` é o ``_id`` do último se HÁ mais, senão ``None``."""

    def __init__(self, collection):
        raise NotImplementedError
