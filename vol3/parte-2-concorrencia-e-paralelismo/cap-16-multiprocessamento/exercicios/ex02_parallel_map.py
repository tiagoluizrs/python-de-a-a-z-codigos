"""Exercício 2: um map paralelo com processos."""


def parallel_map(func, items, processes=2, chunksize=None):
    """Aplica ``func`` (precisa ser picklável: função de módulo) a cada item com um
    ``multiprocessing.Pool`` de ``processes`` processos e devolve a lista NA ORDEM.

    * ``items`` vazio devolve ``[]`` SEM criar processos;
    * ``chunksize=None`` usa ``max(1, ceil(n / (processes * 4)))``;
    * uma exceção da ``func`` se propaga para quem chamou;
    * o ``Pool`` deve ser FECHADO sempre (``with``);
    * ``processes < 1`` levanta ``ValueError``."""
    raise NotImplementedError
