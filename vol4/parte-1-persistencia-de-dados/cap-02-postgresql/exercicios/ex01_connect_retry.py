"""Exercício 1: conectar com novas tentativas (o banco ainda está subindo)."""
import time  # noqa: F401

import psycopg  # noqa: F401


def connect_with_retry(connect, attempts=5, delay=0.1, max_delay=2.0, sleep=time.sleep):
    """Chama ``connect()`` (um callable sem argumentos que devolve uma conexão) até
    ``attempts`` vezes.

    * só repete se levantar ``psycopg.OperationalError`` (qualquer outra exceção sobe na hora);
    * entre tentativas, ``sleep(espera)`` com espera ``delay``, ``2*delay``, ``4*delay``...
      limitada a ``max_delay``;
    * esgotadas as tentativas, re-levanta a ÚLTIMA ``OperationalError``;
    * ``attempts < 1`` levanta ``ValueError``;
    * devolve o que ``connect()`` devolveu na primeira tentativa que funcionar."""
    raise NotImplementedError
