"""Exercício 1: normalizar dados planos e achar as inconsistências."""


def split_customers(rows):
    """``rows`` é uma lista de dicionários desnormalizados com ``order_id``, ``customer_id``,
    ``customer_name``, ``customer_city`` e ``total``. Devolve ``(customers, orders)``:

    * ``customers``: ``{customer_id: {"name": ..., "city": ...}}``;
    * ``orders``: lista de ``{"id": order_id, "customer_id": ..., "total": ...}`` na ordem de entrada;
    * se o MESMO ``customer_id`` aparecer com ``name`` ou ``city`` DIFERENTES, levante
      ``ValueError`` cuja mensagem liste os ``customer_id`` em conflito, ordenados e separados
      por vírgula (``"clientes inconsistentes: 1, 7"``);
    * ``order_id`` repetido levanta ``ValueError("pedido duplicado: <id>")``;
    * ``rows`` vazio devolve ``({}, [])``."""
    raise NotImplementedError
