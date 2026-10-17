"""Exercício 3: um rastreador de chamadas com sys.monitoring."""


def trace_calls(func, *args, **kwargs):
    """Executa ``func(*args, **kwargs)`` e devolve ``(resultado, nomes)``,
    onde ``nomes`` é a lista, em ORDEM, dos nomes (``co_name``) das funções
    Python que COMEÇARAM a executar (evento ``PY_START`` de
    ``sys.monitoring``), incluindo ``func`` mas excluindo qualquer função
    definida neste módulo de apoio.

    Requisitos: use ``sys.monitoring.use_tool_id`` com
    ``sys.monitoring.PROFILER_ID``; sempre desligue os eventos, remova o
    callback e libere o id, MESMO se ``func`` levantar exceção (``try/finally``);
    a exceção deve propagar.
    """
    raise NotImplementedError


def count_calls(func, *args, **kwargs):
    """``collections.Counter`` por nome das funções chamadas (usa ``trace_calls``)."""
    raise NotImplementedError
