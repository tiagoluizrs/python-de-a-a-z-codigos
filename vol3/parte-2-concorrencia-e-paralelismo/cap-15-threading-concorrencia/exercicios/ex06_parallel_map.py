"""Exercício 6: um map paralelo com threads, ordenado e com tratamento de erros."""


def threaded_map(func, items, workers=4, stop_on_error=False):
    """Aplica ``func`` a cada item com ``workers`` threads e devolve a lista de
    resultados NA ORDEM de ``items``.

    * se alguma chamada levantar exceção, depois que as threads terminarem
      levante a exceção do MENOR índice (as demais são descartadas);
    * ``stop_on_error=True``: ao ocorrer o primeiro erro, os itens que AINDA NÃO
      começaram não são executados (use um ``threading.Event``);
    * ``workers < 1`` levanta ``ValueError``; ``items`` vazio devolve ``[]`` sem
      criar threads;
    * não use ``concurrent.futures``: threads e uma fila (ou um índice protegido)."""
    raise NotImplementedError
