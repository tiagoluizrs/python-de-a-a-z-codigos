"""Exercício 4: consulta dinâmica segura (promessa do Capítulo 8 do Volume 3)."""


def build_product_query(name_contains=None, min_price=None, max_price=None, category=None,
                        order_by="name", descending=False, limit=50, offset=0):
    """Devolve ``(sql, params)`` para a tabela ``product(id, name, price, category)``.

    * filtros só entram se não forem ``None``: ``name LIKE ? ESCAPE '\\'`` (com ``%``, ``_``
      e ``\\`` do usuário ESCAPADOS e o termo cercado por ``%``), ``price >= ?``,
      ``price <= ?``, ``category = ?``; juntos com ``AND``;
    * ``order_by`` só aceita ``"id"``, ``"name"``, ``"price"`` (senão ``ValueError``);
      ``descending`` escolhe ``DESC``/``ASC``; desempate SEMPRE por ``id``;
    * ``limit`` precisa estar entre 1 e 200 e ``offset >= 0`` (senão ``ValueError``);
      ambos vão como parâmetros;
    * NENHUM valor do usuário pode aparecer no texto SQL."""
    raise NotImplementedError
