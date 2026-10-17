"""Exercício 3: escopo, ``global`` e ``UnboundLocalError``."""

_last_id = 0


def next_id():
    """Devolva 1, 2, 3, ... a cada chamada, usando ``_last_id``.

    Esta versão levanta ``UnboundLocalError``. Descubra por quê e
    conserte (sem trocar a variável por outra estrutura).
    """
    _last_id += 1
    return _last_id


def reset_ids(start=0):
    """Volte o contador para ``start`` (a próxima id será ``start + 1``)."""
    raise NotImplementedError


def unbound_message():
    """Provoque um ``UnboundLocalError`` de propósito e devolva ``str(exc)``.

    Defina uma função interna que LÊ um nome local antes de atribuí-lo,
    chame-a dentro de ``try`` e devolva a mensagem do erro capturado.
    """
    raise NotImplementedError
