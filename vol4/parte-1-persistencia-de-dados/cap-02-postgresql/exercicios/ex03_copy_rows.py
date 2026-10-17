"""Exercício 3: carga em massa com COPY."""


def copy_rows(conn, table, columns, rows):
    """Carrega ``rows`` (iterável de tuplas) em ``table(columns...)`` usando
    ``COPY ... FROM STDIN`` (``cursor.copy`` e ``write_row``), em UMA transação
    (``conn.transaction()``): se qualquer linha falhar, nada fica.

    * nomes de tabela e colunas montados com ``psycopg.sql`` (``Identifier``), nunca com f-string;
    * ``columns`` vazio levanta ``ValueError``;
    * devolve quantas linhas foram carregadas (``0`` para ``rows`` vazio, sem abrir COPY);
    * erros do PostgreSQL (``psycopg.Error``) se propagam."""
    raise NotImplementedError
