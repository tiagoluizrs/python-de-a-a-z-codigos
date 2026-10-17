"""Exercício 3: transferências entre contas sem deadlock."""
import threading  # noqa: F401


class Account:
    """``Account(number, balance)``; cada conta tem a sua trava. ``balance`` é
    lido por propriedade; ``deposit(n)`` e ``withdraw(n)`` são atômicos por conta
    (``withdraw`` levanta ``ValueError`` se faltar saldo ou ``n <= 0``)."""

    def __init__(self, number, balance=0):
        raise NotImplementedError


def transfer(source, target, amount):
    """Move ``amount`` de ``source`` para ``target`` de forma ATÔMICA para quem
    observa as duas contas, SEM deadlock mesmo que outra thread transfira no
    sentido oposto ao mesmo tempo (tome as duas travas em uma ORDEM GLOBAL, pelo
    ``number``). Saldo insuficiente levanta ``ValueError`` e não altera nada.
    ``source is target`` levanta ``ValueError``."""
    raise NotImplementedError
