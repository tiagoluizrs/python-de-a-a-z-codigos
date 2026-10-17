"""Exercício 2: a corrida: o primeiro que der certo ganha."""


def first_success(funcs, workers=None):
    """Executa os callables ``funcs`` (sem argumentos) em ``ThreadPoolExecutor`` e
    devolve o resultado do PRIMEIRO que terminar COM SUCESSO.

    * as falhas de outros são ignoradas enquanto algum puder ter sucesso;
    * se TODOS falharem, levante ``RuntimeError`` com a lista de erros como
      ``args[1]`` (``RuntimeError("todos falharam", [erros...])``);
    * os que ainda não começaram devem ser CANCELADOS quando houver um vencedor
      (``cancel()`` nos futures pendentes);
    * ``funcs`` vazio levanta ``ValueError``; ``workers`` padrão = ``len(funcs)``."""
    raise NotImplementedError
