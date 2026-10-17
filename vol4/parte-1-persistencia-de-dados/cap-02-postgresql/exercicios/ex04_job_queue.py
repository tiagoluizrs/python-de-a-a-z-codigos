"""Exercício 4: uma fila de tarefas no PostgreSQL com SKIP LOCKED."""


def create_schema(conn):
    """Cria ``job(id bigserial PRIMARY KEY, payload text NOT NULL, state text NOT NULL
    DEFAULT 'new' CHECK (state IN ('new', 'running', 'done')), owner text)`` e confirma."""
    raise NotImplementedError


def enqueue(conn, payloads):
    """Insere uma tarefa por item de ``payloads`` (em uma transação) e devolve a lista de ids."""
    raise NotImplementedError


def claim(conn, worker, limit=5, hold=0.0):
    """Reserva até ``limit`` tarefas ``new`` para ``worker``: troca para ``running`` e grava
    ``owner``, na ordem do ``id``, usando ``FOR UPDATE SKIP LOCKED`` (vários trabalhadores
    simultâneos NUNCA pegam a mesma tarefa e NUNCA esperam um pelo outro).
    Tudo em uma transação (``conn.transaction()``); ``hold`` segundos de ``time.sleep``
    ANTES de confirmar (gancho para os testes). Devolve a lista de ids reservados (ordenada)."""
    raise NotImplementedError


def finish(conn, job_id, worker):
    """Marca como ``done`` SE a tarefa estiver ``running`` e for do ``worker``. ``True`` se
    mudou, ``False`` caso contrário."""
    raise NotImplementedError
