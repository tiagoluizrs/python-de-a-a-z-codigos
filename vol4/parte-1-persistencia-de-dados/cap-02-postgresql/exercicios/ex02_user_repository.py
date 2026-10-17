"""Exercício 2: um repositório de usuários com paginação por chave (keyset)."""


class UserRepository:
    """``UserRepository(conn)``; ``conn`` usa ``row_factory=dict_row`` e ``autocommit=False``.

    * ``create_schema()``: tabela ``app_user(id bigserial PRIMARY KEY, email text NOT NULL,
      name text NOT NULL, created_at timestamptz NOT NULL DEFAULT now())`` e um índice
      ÚNICO sobre ``lower(email)``; confirma a transação;
    * ``add(email, name)`` -> dicionário da linha criada (``RETURNING *``); e-mail repetido
      (ignorando maiúsculas) levanta ``ValueError`` e a conexão continua utilizável;
    * ``get_by_email(email)`` -> dicionário ou ``None`` (ignora maiúsculas);
    * ``rename(user_id, name)`` -> ``True`` se atualizou;
    * ``page(after_id=None, limit=3)`` -> ``(linhas, proximo)``: as ``limit`` primeiras
      linhas com ``id > after_id`` ordenadas por ``id``; ``proximo`` é o ``id`` da última
      linha se HOUVER mais linhas depois dela, senão ``None`` (busque ``limit + 1`` para saber);
    * toda escrita é confirmada; tudo com parâmetros ``%s``."""

    def __init__(self, conn):
        raise NotImplementedError
