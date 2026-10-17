"""Exercício 4: ler planos de consulta para testá-los."""


def plan_report(conn, sql, params=()):
    """Roda ``EXPLAIN QUERY PLAN`` e devolve um dicionário:

    * ``"scans"``: lista ORDENADA dos nomes das tabelas varridas por inteiro (``SCAN <tabela>``);
    * ``"searches"``: lista ORDENADA de ``(tabela, índice)`` das buscas por índice
      (``SEARCH <tabela> USING [COVERING] INDEX <índice> ...``; para a chave primária inteira
      use o índice ``"PRIMARY KEY"``);
    * ``"temp_btree"``: ``True`` se o plano usa ``USE TEMP B-TREE`` (ordenação/agrupamento sem índice);
    * ``"uses_index"``: ``True`` se ``searches`` não é vazio.
    Ignore as subconsultas escalares na ordem em que aparecem: apenas percorra TODAS as linhas do plano."""
    raise NotImplementedError


def assert_uses_index(conn, sql, params=(), table=None):
    """Levanta ``AssertionError`` com uma mensagem útil se o plano de ``sql`` varre ``table`` por inteiro
    (ou, com ``table=None``, qualquer tabela). Devolve ``None`` se estiver tudo certo."""
    raise NotImplementedError
