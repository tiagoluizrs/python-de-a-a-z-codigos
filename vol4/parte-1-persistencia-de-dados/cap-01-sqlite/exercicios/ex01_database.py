"""Exercício 1: abrir o banco do jeito certo e um gerenciador de transações."""
import contextlib  # noqa: F401
import sqlite3  # noqa: F401


def open_database(path=":memory:"):
    """Abre uma conexão ``sqlite3`` pronta para uso:

    * ``isolation_level=None`` (você controla BEGIN/COMMIT);
    * ``row_factory = sqlite3.Row``;
    * ``PRAGMA foreign_keys = ON`` e ``PRAGMA busy_timeout = 5000``;
    * se ``path`` NÃO for ``":memory:"``, ``PRAGMA journal_mode = WAL``."""
    raise NotImplementedError


@contextlib.contextmanager
def transaction(conn):
    """Gerenciador de contexto para transações que podem ser ANINHADAS.

    * fora de qualquer transação: ``BEGIN IMMEDIATE`` ... ``COMMIT`` (ou ``ROLLBACK``
      se o bloco levantar);
    * dentro de uma transação (``conn.in_transaction``): um ``SAVEPOINT`` com nome
      único; se o bloco interno levantar, ``ROLLBACK TO`` + ``RELEASE`` desfazem só
      o interno (a exceção sobe);
    * exceções sempre se propagam."""
    raise NotImplementedError
    yield  # pragma: no cover
