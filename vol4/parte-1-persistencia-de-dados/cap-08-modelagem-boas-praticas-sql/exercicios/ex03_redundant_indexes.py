"""Exercício 3: índices redundantes."""


def redundant_indexes(conn):
    """Lista ORDENADA de tuplas ``(tabela, índice_redundante, coberto_por)`` para um banco SQLite.

    Um índice A é REDUNDANTE em relação a B (mesma tabela) quando as colunas de A são um PREFIXO
    (da esquerda) das colunas de B, e A não é ÚNICO (um índice único tem papel de restrição),
    e B diferente de A. Se vários índices cobrem A, ``coberto_por`` é o de MENOS colunas (empate:
    o de menor nome). Para índices com as MESMAS colunas (duplicados), o de nome MAIOR é o
    redundante e o de nome menor o cobre (o de nome menor NÃO é redundante por causa do duplicado). Ignore índices
    parciais (``WHERE``) e índices criados automaticamente (``sqlite_autoindex_*``).
    Use ``PRAGMA index_list`` e ``PRAGMA index_info``."""
    raise NotImplementedError
