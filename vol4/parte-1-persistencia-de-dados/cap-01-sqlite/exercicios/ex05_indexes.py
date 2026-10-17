"""Exercício 5: ler o plano de execução e criar índices."""


def uses_index(conn, sql, params=()):
    """``True`` se o plano (``EXPLAIN QUERY PLAN``) de ``sql`` usa um índice
    (``USING INDEX``, ``USING COVERING INDEX`` ou ``USING INTEGER PRIMARY KEY``);
    ``False`` se for varredura completa (``SCAN``)."""
    raise NotImplementedError


def ensure_index(conn, table, column, unique=False):
    """Cria ``ix_<table>_<column>`` (``UNIQUE`` se ``unique``) com ``IF NOT EXISTS``.
    Devolve ``True`` se CRIOU agora e ``False`` se já existia. Valide os nomes com
    ``^[A-Za-z_][A-Za-z0-9_]*$`` (``ValueError``); tabela ou coluna inexistente
    levanta ``ValueError`` (consulte ``PRAGMA table_info``)."""
    raise NotImplementedError
