"""Exercício 5: paginação por chave com várias colunas de ordenação."""


def keyset_page(conn, table, order_columns, after=None, limit=10, columns="*"):
    """Paginação por chave (``keyset``) em SQLite, estável com empates.

    * ``order_columns``: lista de colunas na ordem desejada, crescente; a ÚLTIMA deve ser única
      (normalmente o ``id``) para desempatar; nomes validados com ``^[A-Za-z_][A-Za-z0-9_]*$``
      (``ValueError``); lista vazia levanta ``ValueError``;
    * ``after``: tupla com os valores das ``order_columns`` da ÚLTIMA linha da página anterior
      (``None`` na primeira página); use a comparação de linhas ``(a, id) > (?, ?)``;
    * ``limit`` de 1 a 1000 (``ValueError``);
    * devolve ``(linhas, proximo)`` onde ``linhas`` é uma lista de tuplas (``columns`` é texto SQL FIXO
      dado por você) e ``proximo`` é a tupla de valores de ``order_columns`` da última linha SE existirem
      mais linhas (busque ``limit + 1``), senão ``None``;
    * se ``columns != "*"``, ``columns`` PRECISA conter todas as ``order_columns`` (para montar ``proximo``): senão ``ValueError``."""
    raise NotImplementedError
