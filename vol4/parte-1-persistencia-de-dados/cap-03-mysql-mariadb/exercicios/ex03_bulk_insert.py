"""Exercício 3: carga em lotes com nomes citados com segurança."""


def quote_identifier(name):
    """Devolve ``name`` entre crases, dobrando as crases internas (``a`b`` -> ```a``b```).
    ``name`` vazio, com ``\\x00`` ou maior que 64 caracteres levanta ``ValueError``."""
    raise NotImplementedError


def bulk_insert(conn, table, columns, rows, batch_size=1000):
    """Insere ``rows`` (iterável de tuplas) em ``table(columns...)``, nomes citados com
    ``quote_identifier``, usando ``executemany`` em lotes de ``batch_size``, tudo em UMA
    transação (falhou: nada fica, o erro sobe). Devolve quantas linhas entraram (``0`` se
    ``rows`` vazio). ``columns`` vazio ou ``batch_size < 1`` levantam ``ValueError``."""
    raise NotImplementedError
