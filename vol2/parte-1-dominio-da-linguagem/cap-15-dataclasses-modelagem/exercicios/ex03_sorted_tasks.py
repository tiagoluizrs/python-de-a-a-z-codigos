"""Exercício 3: ordenação por campos escolhidos."""


class Task:
    """``@dataclass(order=True)`` ordenada por PRIORIDADE (maior primeiro) e,
    em empate, por NOME (A a Z).

    Campos: ``priority: int`` e ``name: str``, mais ``done: bool`` (padrão
    ``False``), que NÃO participa da comparação nem do ``repr``.

    Dica: crie um campo ``sort_index: tuple`` com ``field(init=False,
    repr=False)`` preenchido em ``__post_init__``, e deixe os demais campos com
    ``compare=False``.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
