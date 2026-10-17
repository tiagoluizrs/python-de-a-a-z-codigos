"""Exercício 1: inverter um dicionário com valores repetidos."""


def invert(mapping: dict) -> dict:
    """Inverta ``mapping``: cada valor vira chave e aponta para a LISTA
    das chaves originais que o tinham, na ordem de inserção.

    ``invert({"Ana": "A", "Bia": "B", "Caio": "A"})``
    devolve ``{"A": ["Ana", "Caio"], "B": ["Bia"]}``.

    Os valores do original precisam ser hasheáveis. Não modifique a entrada.
    Dica: ``dict.setdefault(chave, []).append(...)``.
    """
    raise NotImplementedError
