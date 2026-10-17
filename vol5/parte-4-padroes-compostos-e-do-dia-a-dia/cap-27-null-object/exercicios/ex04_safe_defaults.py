"""Exercício 4: a ausência sem ``if``: valores padrão, coleções vazias, ``nullcontext``, ``NullHandler`` e uma função que não faz nada."""
import contextlib
import logging


def names_of(users) -> list[str]:
    """``users`` é uma lista de dicionários ``{"name": ...}`` OU ``None`` (ninguém). Devolve a lista de nomes, e ``[]`` para ``None`` (nunca ``None``). Vazio continua vazio."""
    raise NotImplementedError


def first_or(iterable, default=None):
    """O primeiro item de ``iterable`` (qualquer iterável, inclusive um gerador, do qual você consome NO MÁXIMO um item), ou ``default`` se está vazio. ``iterable`` ``None``: ``default``."""
    raise NotImplementedError


def setting(config, path: str, default=None):
    """Lê ``config`` (dicionários aninhados) por um caminho com pontos: ``setting({"db": {"port": 0}}, "db.port", 5432)`` é ``0``. O valor que EXISTE é devolvido como está, mesmo
    ``0``, ``""``, ``False`` ou ``None`` (o ``default`` só vale se o caminho NÃO existe; o erro clássico é usar ``valor or default``). Se um passo do meio não é um dicionário
    (``setting({"a": 1}, "a.b")``): ``default``. ``config`` ``None``: ``default``."""
    raise NotImplementedError


def locked(lock=None):
    """Para usar como ``with locked(lock):``. Devolve o próprio ``lock`` se foi dado (``is not None``: uma trava pode ser falsa) e ``contextlib.nullcontext()`` se ``lock`` é ``None``."""
    raise NotImplementedError


def quiet_logger(name: str) -> logging.Logger:
    """Devolve ``logging.getLogger(name)`` configurado para NÃO emitir nada: exatamente UM handler (um ``logging.NullHandler``, trocando os que existiam) e ``propagate = False``.
    Chamar de novo para o mesmo nome deixa continuar exatamente um handler."""
    raise NotImplementedError


def run_tasks(tasks, on_progress=None) -> list:
    """Executa cada função de ``tasks`` (sem argumentos) e devolve a lista dos resultados. Depois de CADA tarefa chama ``on_progress(i, total, resultado)`` (``i`` de ``1``); sem
    ``on_progress`` (``None``) a função usa uma que não faz nada, e NÃO há ``if on_progress`` dentro do laço. Se uma tarefa levantar uma exceção, ela sobe na hora (as seguintes não rodam)."""
    raise NotImplementedError
