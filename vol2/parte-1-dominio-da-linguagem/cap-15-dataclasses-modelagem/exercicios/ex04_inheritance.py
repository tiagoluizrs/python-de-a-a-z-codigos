"""Exercício 4: herança de dataclasses com kw_only."""


class Entity:
    """``@dataclass`` com ``id: int`` e ``created: str`` (padrão ``"hoje"``)."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Customer:
    """Subclasse de ``Entity`` (``@dataclass(kw_only=True)``) com ``name: str``
    OBRIGATÓRIO e ``vip: bool`` (padrão ``False``).

    ``Customer(1, name="Ana")`` e ``Customer(id=1, name="Ana", vip=True)``
    funcionam; ``Customer(1, "Ana")`` levanta ``TypeError``. ``Customer``
    deve ser subclasse de ``Entity``.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
