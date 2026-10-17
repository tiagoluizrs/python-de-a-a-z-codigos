"""Exercício 5: ordem de construção com graphlib."""


def build_layers(deps):
    """``deps`` mapeia cada tarefa ao conjunto de tarefas de que depende.

    Devolve uma lista de **camadas**: cada camada é uma lista ORDENADA com as
    tarefas que podem rodar em paralelo, e só dependem de camadas anteriores.
    Dependências que não aparecem como chave também entram (sem dependências).
    Em caso de ciclo, levanta ``ValueError`` com a mensagem ``"ciclo: a -> b
    -> a"`` (os nós do ciclo, na ordem em que o ``CycleError`` os informa).
    Use ``graphlib.TopologicalSorter``.
    """
    raise NotImplementedError


def critical_path_length(deps):
    """Número de camadas de ``build_layers(deps)`` (o mínimo de etapas
    sequenciais), ``0`` se vazio."""
    raise NotImplementedError
