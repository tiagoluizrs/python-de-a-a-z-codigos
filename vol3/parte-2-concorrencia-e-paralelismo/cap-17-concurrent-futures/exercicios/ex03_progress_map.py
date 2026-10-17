"""Exercício 3: map com progresso, mantendo a ordem."""


def map_with_progress(executor, func, items, on_progress=None):
    """Submete ``func(item)`` ao ``executor`` (já criado pelo chamador) e devolve a lista
    de resultados NA ORDEM de ``items``.

    * ``on_progress(feitos, total)`` é chamado após cada tarefa terminar (na ordem
      de TÉRMINO), com ``feitos`` de 1 até ``total``;
    * a primeira exceção levantada por uma tarefa é re-levantada, mas SÓ depois de
      cancelar as tarefas ainda pendentes;
    * ``items`` vazio devolve ``[]`` sem chamar ``on_progress``."""
    raise NotImplementedError
