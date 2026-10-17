"""Exercício 2: um linter de esquema para SQLite."""


def schema_smells(conn):
    """Examina o banco SQLite (``sqlite_master`` e ``PRAGMA``) e devolve uma lista ORDENADA de tuplas
    ``(código, tabela, coluna)`` (``coluna`` é ``None`` quando não se aplica):

    * ``"sem_chave_primaria"``: tabela comum sem nenhuma coluna na PK (ignore tabelas ``sqlite_*``);
    * ``"fk_sem_indice"``: coluna de chave estrangeira (``PRAGMA foreign_key_list``) que NÃO é a
      primeira coluna de nenhum índice da tabela nem faz parte da PK como primeira coluna;
    * ``"dinheiro_em_float"``: coluna ``REAL``/``FLOAT``/``DOUBLE`` cujo nome (minúsculo) contém
      ``price``, ``preco``, ``amount``, ``valor``, ``total``, ``balance`` ou ``saldo``;
    * ``"coluna_nula_na_pk_unica"``: coluna de um índice ÚNICO que aceita NULL (``notnull = 0``)
      e não é chave primária (a unicidade com NULL não garante nada).
    Banco sem problemas devolve ``[]``."""
    raise NotImplementedError
