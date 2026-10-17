"""Exercício 4: contexto de log com contextvars."""
import contextvars
import logging

# Dicionário imutável do contexto atual (não altere o dict: crie um novo)
CONTEXT = contextvars.ContextVar("log_context", default={})


def log_context(**fields):
    """Gerenciador de contexto (use ``@contextlib.contextmanager``): dentro
    do ``with``, o contexto atual é o anterior ATUALIZADO com ``fields``;
    ao sair (mesmo com exceção) volta ao anterior (``ContextVar.reset``).
    Contextos aninhados se acumulam."""
    raise NotImplementedError


class ContextFilter(logging.Filter):
    """Copia cada campo do contexto atual para o registro (``record.<campo>``),
    SEM sobrescrever atributos que o registro já tenha, e garante que existe
    ``record.request_id`` (``"-"`` se o contexto não tiver). Devolve ``True``."""

    def filter(self, record):
        raise NotImplementedError
