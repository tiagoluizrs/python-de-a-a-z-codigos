"""Exercício 3: cache que não prende memória."""


class Document:
    """Objeto pesado que queremos reaproveitar enquanto alguém o usa."""

    def __init__(self, name: str) -> None:
        self.name = name


class WeakCache:
    """Cache de ``Document`` por nome, baseado em referências fracas.

    - ``get(name)`` devolve a MESMA instância enquanto alguém a mantiver viva;
    - quando ninguém mais a referencia, a entrada some sozinha;
    - ``created`` conta quantos ``Document`` foram construídos;
    - ``len(cache)`` informa quantas entradas vivas existem.

    Dica: ``weakref.WeakValueDictionary``.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def get(self, name: str) -> Document:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
