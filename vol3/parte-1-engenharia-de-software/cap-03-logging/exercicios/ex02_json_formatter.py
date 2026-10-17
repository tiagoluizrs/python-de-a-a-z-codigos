"""Exercício 2: um Formatter que produz uma linha de JSON."""
import logging


class JsonFormatter(logging.Formatter):
    """``format(record)`` devolve uma string JSON (uma linha) com as chaves,
    NESTA ordem: ``"time"`` (UTC, ISO 8601 com milissegundos e ``Z``:
    ``"1970-01-01T00:00:00.000Z"`` para ``record.created == 0``),
    ``"level"`` (nome), ``"logger"``, ``"message"`` (já com os argumentos
    aplicados); depois os atributos EXTRAS do registro (os que não existem em
    um ``LogRecord`` comum, ordenados pelo nome); por fim ``"exc"`` com o
    traceback formatado, se houver ``exc_info``.

    Valores que não são serializáveis em JSON viram ``str(valor)``; caracteres
    não ASCII ficam como estão (``ensure_ascii=False``)."""

    def format(self, record):
        raise NotImplementedError
