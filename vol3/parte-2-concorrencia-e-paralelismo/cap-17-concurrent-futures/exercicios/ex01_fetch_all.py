"""Exercício 1: executar um lote sem que um erro derrube os outros."""
from dataclasses import dataclass


@dataclass
class Outcome:
    """``index`` (posição na entrada), ``value`` (resultado ou ``None``) e ``error``
    (a exceção ou ``None``); ``ok`` é ``True`` quando ``error is None``."""
    index: int
    value: object = None
    error: Exception | None = None

    @property
    def ok(self):
        return self.error is None


def fetch_all(func, items, workers=4):
    """Executa ``func(item)`` para cada item com um ``ThreadPoolExecutor`` e devolve
    uma lista de ``Outcome`` NA ORDEM de ``items`` (um por item). Exceções das
    chamadas (``Exception``) viram ``Outcome.error``; NUNCA propague. ``items``
    vazio devolve ``[]``; ``workers < 1`` levanta ``ValueError``."""
    raise NotImplementedError
