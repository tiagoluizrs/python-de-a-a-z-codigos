"""Exercício 5: suprimir mensagens repetidas."""
import logging
import time


class DuplicateFilter(logging.Filter):
    """Evita inundar o log com a mesma mensagem.

    A identidade de uma mensagem é ``(record.name, record.levelno,
    record.getMessage())``. Regras (``window`` em segundos, medido por
    ``clock()``, que o teste substitui):

    * a primeira ocorrência passa e abre uma janela;
    * ocorrências IGUAIS dentro da janela são suprimidas (``filter`` devolve
      ``False``) e contadas;
    * a primeira ocorrência DEPOIS da janela passa de novo, com o texto
      acrescido de ``" (+N repetidas)"`` se houve ``N > 0`` supressões
      (altere ``record.msg`` e zere ``record.args``), e abre nova janela;
    * mensagens diferentes não se afetam.
    """

    def __init__(self, window=5.0, clock=time.monotonic):
        super().__init__()
        raise NotImplementedError

    def filter(self, record):
        raise NotImplementedError
