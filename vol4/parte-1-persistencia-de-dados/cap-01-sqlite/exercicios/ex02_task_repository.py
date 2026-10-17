"""Exercício 2: um repositório de tarefas sobre SQLite."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


class TaskRepository:
    """``TaskRepository(conn)`` (conexão com ``row_factory = sqlite3.Row``).

    * ``create_schema()``: tabela ``task(id INTEGER PRIMARY KEY, title TEXT NOT NULL
      UNIQUE CHECK (length(trim(title)) > 0), done INTEGER NOT NULL DEFAULT 0)``;
    * ``add(title)`` -> ``Task`` (use ``RETURNING``); título duplicado ou em branco
      levanta ``ValueError``;
    * ``get(id)`` -> ``Task`` ou ``None``;
    * ``list(done=None)`` -> lista ordenada por ``id`` (``done`` ``True``/``False`` filtra);
    * ``complete(id)`` -> ``True`` se existia e ainda não estava feita (``False`` caso
      contrário);
    * ``delete(id)`` -> ``True`` se removeu;
    * ``stats()`` -> ``{"total": n, "done": n, "pending": n}`` (zeros em tabela vazia).
    Sempre com parâmetros ``?``; cada operação de escrita deve ser confirmada."""

    def __init__(self, conn):
        raise NotImplementedError
