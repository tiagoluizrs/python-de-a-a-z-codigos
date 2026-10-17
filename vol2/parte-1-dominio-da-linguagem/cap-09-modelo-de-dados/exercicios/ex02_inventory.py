"""Exercício 2: um contêiner completo."""


class Inventory:
    """Estoque (sku -> quantidade) com o protocolo de contêiner.

    * ``Inventory(apple=3)`` aceita itens iniciais por nome;
    * ``len``, ``in``, iteração (sobre os skus, na ordem de inserção);
    * ``inv["apple"]`` levanta ``KeyError`` se não existir;
    * ``inv["apple"] = n``: ``n`` deve ser um inteiro >= 0, senão
      ``ValueError``; ``n == 0`` REMOVE o item;
    * ``del inv["apple"]`` e ``bool(inv)`` (falso se vazio);
    * ``repr`` no formato ``Inventory({'apple': 3})``.
    """

    def __init__(self, **stock):
        raise NotImplementedError
