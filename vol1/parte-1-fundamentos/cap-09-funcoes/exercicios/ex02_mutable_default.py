"""Exercício 2: corrigir a armadilha do valor padrão mutável."""


def add_tag(tag, tags=[]):
    """Acrescente ``tag`` a ``tags`` e devolva a lista.

    Comportamento desejado:

    - se o chamador passar uma lista, ela é alterada no lugar e devolvida;
    - se não passar nada, cada chamada começa com uma lista NOVA;
    - se passar ``None``, também começa com uma lista nova.

    A versão abaixo está errada: o padrão ``[]`` é criado uma única vez.
    Corrija-a (o padrão deve deixar de ser uma lista).
    """
    tags.append(tag)
    return tags


def first_or(items, default=None):
    """Devolva o primeiro item de ``items``.

    Se ``items`` estiver vazio: devolva ``default`` quando ele for
    informado (mesmo que seja ``None``) e levante ``ValueError`` quando
    NÃO for informado. Dica: use ``sentinel("MISSING")`` (3.15) como
    padrão, já que ``None`` é um valor legítimo aqui.
    """
    raise NotImplementedError
