"""Exercício 4: um Protocol checável em tempo de execução."""
from typing import Protocol


class SupportsClose(Protocol):
    """Qualquer objeto com ``close()``.

    Marque-o para poder usar ``isinstance`` (``runtime_checkable``).
    """

    def close(self) -> None: ...


def close_all(items):
    """Feche os itens que cumprem o protocolo e devolva quantos foram fechados.

    Itens que NÃO têm ``close()`` são ignorados. Use ``isinstance`` com o
    protocolo (e não ``hasattr``). Se um ``close()`` levantar exceção, as
    DEMAIS devem ser fechadas mesmo assim, e a primeira exceção deve ser
    relançada no fim.
    """
    raise NotImplementedError
