"""Gabarito do exercício 2."""

MISSING = sentinel("MISSING")


def add_tag(tag, tags=None):
    # None significa "o chamador não passou lista": criamos uma por chamada
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def first_or(items, default=MISSING):
    for item in items:
        return item
    # comparamos por identidade: None também é um default válido
    if default is MISSING:
        raise ValueError("empty sequence and no default given")
    return default
