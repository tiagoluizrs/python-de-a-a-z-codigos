"""Gabarito do exercício 5."""


def remove_in_place(items: list, predicate) -> int:
    before = len(items)
    items[:] = [item for item in items if not predicate(item)]   # mesma lista, novo conteúdo
    return before - len(items)
