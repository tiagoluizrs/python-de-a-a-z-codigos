"""Exercício 4: 'or' descarta valores válidos."""


def coalesce(*values, default=None):
    """Devolva o primeiro valor que NÃO é ``None``; se todos forem ``None``
    (ou não houver valores), devolva ``default``.

    Diferente de ``a or b or c``, valores como ``0``, ``""`` e ``[]`` são
    válidos e devem ser devolvidos. Exemplo: ``coalesce(None, 0, 5) == 0``.
    """
    raise NotImplementedError
