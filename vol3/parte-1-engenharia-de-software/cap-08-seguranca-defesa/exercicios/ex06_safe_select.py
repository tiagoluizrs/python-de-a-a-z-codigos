"""Exercício 6: um SELECT seguro (parâmetros para valores, lista de permissão para nomes)."""


def select_where(conn, table, allowed, filters, order_by=None, limit=None):
    """Executa ``SELECT * FROM <table> [WHERE ...] [ORDER BY ...] [LIMIT ?]`` em
    uma conexão ``sqlite3`` e devolve ``fetchall()``.

    * ``allowed``: ``{tabela: {colunas permitidas}}``; tabela ou coluna fora
      dele (em ``filters`` ou ``order_by``) levanta ``ValueError``;
    * ``filters``: ``dict`` ``coluna -> valor``, combinados com ``AND``:
      ``None`` vira ``coluna IS NULL``; lista/tupla vira ``coluna IN (?, ?)``
      (vazia: nenhuma linha, ``1 = 0``); o resto, ``coluna = ?``;
    * ``order_by``: ``"coluna"`` (crescente) ou ``"-coluna"`` (decrescente);
    * ``limit``: inteiro >= 0 (``bool`` não vale) ou ``None``;
    * TODO valor vai por parâmetro ``?``; os nomes (já validados) entram no
      texto da consulta."""
    raise NotImplementedError
