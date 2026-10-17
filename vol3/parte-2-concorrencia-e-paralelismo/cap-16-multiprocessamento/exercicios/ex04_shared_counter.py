"""Exercício 4: um contador compartilhado entre PROCESSOS."""


def count_with_processes(processes, per_process):
    """Use o contexto ``spawn``: crie um ``Value("i", 0)`` e um ``Lock()``; inicie
    ``processes`` processos, cada um executando
    ``tasks.increment(value, lock, per_process)``; espere todos terminarem e
    devolva o valor final (que deve ser ``processes * per_process``).
    ``processes < 1`` ou ``per_process < 0`` levantam ``ValueError``."""
    raise NotImplementedError
