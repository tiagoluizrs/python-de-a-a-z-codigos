"""Exercício 3: filtros de logging."""
import logging


class RedactFilter(logging.Filter):
    """Esconde valores de campos sensíveis na MENSAGEM.

    ``RedactFilter(keys=("password", "token"))``: em ``record.getMessage()``,
    trechos como ``password=abc``, ``password: abc``, ``PASSWORD = "a b"``
    (sem diferenciar caixa) viram ``password=***`` (o nome da chave mantém a
    caixa original). Só casa a chave como palavra inteira (``mypassword=x``
    NÃO muda). O filtro grava o texto novo em ``record.msg``, zera
    ``record.args`` e SEMPRE devolve ``True``."""

    def __init__(self, keys=("password", "token", "secret")):
        super().__init__()
        raise NotImplementedError

    def filter(self, record):
        raise NotImplementedError


class LevelRangeFilter(logging.Filter):
    """Deixa passar só registros com ``minimum <= levelno <= maximum``
    (``maximum=None`` significa sem limite superior). Útil para mandar INFO
    para a saída padrão e WARNING+ para a de erro."""

    def __init__(self, minimum=logging.NOTSET, maximum=None):
        super().__init__()
        raise NotImplementedError

    def filter(self, record):
        raise NotImplementedError
