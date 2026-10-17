"""Exercício 6: exclusão lógica com índice único parcial (SQLite)."""


class SoftDeleteUsers:
    """``SoftDeleteUsers(conn)``.

    * ``create_schema()``: tabela ``app_user(id INTEGER PRIMARY KEY, email TEXT NOT NULL,
      name TEXT NOT NULL, deleted_at TEXT)`` e um índice ÚNICO PARCIAL em ``lower(email)`` apenas
      ``WHERE deleted_at IS NULL``; também uma VIEW ``active_user`` com os não apagados;
    * ``add(email, name)`` -> ``id``; e-mail ativo repetido (ignorando maiúsculas) levanta
      ``ValueError`` (``sqlite3.IntegrityError`` traduzido);
    * ``delete(user_id, now)`` -> ``True`` se marcou como apagado (``deleted_at = now``, texto ISO), ``False``
      se não existia ou já estava apagado;
    * ``restore(user_id)`` -> ``True`` se restaurou; levanta ``ValueError`` se já existe OUTRO usuário
      ativo com o mesmo e-mail (ignorando maiúsculas); ``False`` se não estava apagado/não existe;
    * ``purge(before_iso)`` -> quantos registros APAGADOS (``deleted_at < before_iso``) foram removidos
      de vez; nunca toca nos ativos;
    * ``active_emails()`` -> lista ordenada dos e-mails ativos, lendo a VIEW;
    * todas as escritas são confirmadas (``commit``)."""

    def __init__(self, conn):
        raise NotImplementedError
