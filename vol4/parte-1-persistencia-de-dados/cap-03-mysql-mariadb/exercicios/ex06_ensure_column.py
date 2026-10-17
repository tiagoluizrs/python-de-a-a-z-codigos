"""Exercício 6: DDL idempotente (o MySQL não tem ADD COLUMN IF NOT EXISTS)."""


def column_exists(conn, table, column):
    """``True`` se ``column`` existir em ``table`` no banco ATUAL (``DATABASE()``),
    consultando ``information_schema.COLUMNS`` com parâmetros ``%s``."""
    raise NotImplementedError


def ensure_column(conn, table, column, definition):
    """Se a coluna não existir, executa ``ALTER TABLE `table` ADD COLUMN `column` definition``
    e devolve ``True``; se já existir, ``False``. Nomes validados (``[A-Za-z_][A-Za-z0-9_]*``;
    senão ``ValueError``); ``definition`` é texto SQL FIXO escrito por você (não valide;
    nunca passe dado de usuário). Lembre: o DDL confirma sozinho no MySQL."""
    raise NotImplementedError
