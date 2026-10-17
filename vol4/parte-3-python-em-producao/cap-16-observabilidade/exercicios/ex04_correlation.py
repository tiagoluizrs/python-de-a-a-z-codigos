"""Exercício 4: o id da requisição preso ao contexto (``contextvars``): threads, tarefas assíncronas e logs."""
import logging


def get_request_id() -> str:
    """O id da requisição atual, ou ``"-"`` se não houver nenhuma."""
    raise NotImplementedError


class request_context:
    """Gerenciador de contexto: ``with request_context("req-1"): ...`` define o id da requisição e, ao sair, RESTAURA o
    anterior (também em caso de exceção e em usos aninhados)."""

    def __init__(self, request_id: str):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc):
        raise NotImplementedError


class RequestIdFilter(logging.Filter):
    """Um filtro do ``logging`` que acrescenta ``record.request_id`` (o id atual) a TODOS os registros e deixa passar
    (``filter`` devolve ``True``)."""

    def filter(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError


async def fan_out(request_id: str, count: int) -> list[str]:
    """Dentro de ``request_context(request_id)``, dispare ``count`` tarefas assíncronas CONCORRENTES
    (``asyncio.create_task``/``gather``), cada uma devolvendo ``get_request_id()`` depois de um ``await asyncio.sleep(0)``.
    Devolva a lista dos ids vistos (todos devem ser ``request_id``: as tarefas herdam o contexto)."""
    raise NotImplementedError


def run_in_thread(fn, *args):
    """Executa ``fn(*args)`` em uma NOVA thread que ENXERGA o contexto atual (id da requisição incluso) e devolve o
    resultado de ``fn``. Uma thread nova NÃO herda o contexto sozinha: use ``contextvars.copy_context()``."""
    raise NotImplementedError
