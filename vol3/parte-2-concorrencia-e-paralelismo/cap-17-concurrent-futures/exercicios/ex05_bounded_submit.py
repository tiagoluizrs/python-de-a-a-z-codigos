"""Exercício 5: limitar quantas tarefas ficam em voo (contrapressão)."""


def bounded_map(executor, func, items, max_pending=8):
    """Como ``executor.map``, mas NUNCA com mais de ``max_pending`` tarefas
    submetidas e ainda não concluídas (útil para entradas enormes ou geradores
    infinitos). Devolve a lista de resultados NA ORDEM de ``items``.

    * ``items`` pode ser um iterável qualquer (consuma-o aos poucos);
    * use ``concurrent.futures.wait(..., return_when=FIRST_COMPLETED)`` para abrir
      espaço antes de submeter a próxima;
    * exceções de tarefas se propagam (depois de cancelar as pendentes);
    * ``max_pending < 1`` levanta ``ValueError``."""
    raise NotImplementedError
