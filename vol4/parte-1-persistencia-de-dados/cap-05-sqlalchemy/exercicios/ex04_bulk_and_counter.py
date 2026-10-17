"""Exercício 4: carga em lotes e um contador de consultas."""
from contextlib import contextmanager  # noqa: F401


class QueryCounter:
    """Gerenciador de contexto que conta os comandos SQL executados por um ``Engine``.

    * ``with QueryCounter(engine) as counter:``; dentro do bloco, ``counter.count`` (int) e
      ``counter.statements`` (lista de textos SQL) crescem a cada comando (evento
      ``before_cursor_execute``);
    * ao sair, REMOVE o ouvinte (``event.remove``): depois do bloco, nada mais é contado;
    * ``executemany`` conta como UM comando."""

    def __init__(self, engine):
        raise NotImplementedError


def bulk_create_customers(session, m, rows, batch_size=1000):
    """Insere ``rows`` (lista de dicionários ``name``/``email``) com ``session.execute(insert(m.Customer), lote)``
    em lotes de ``batch_size`` e UM ``commit`` no fim. Devolve a quantidade inserida (``0`` se
    vazio). Se qualquer lote falhar, ``rollback`` (nada fica) e o erro sobe.
    ``batch_size < 1`` levanta ``ValueError``."""
    raise NotImplementedError
