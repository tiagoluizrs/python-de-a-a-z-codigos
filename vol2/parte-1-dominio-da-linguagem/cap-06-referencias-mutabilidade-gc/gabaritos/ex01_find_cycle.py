"""Gabarito do exercício 1."""

ATOMIC = (int, float, complex, str, bytes, bool, type(None))


def _children(obj):
    if isinstance(obj, dict):
        return list(obj.keys()) + list(obj.values())
    if isinstance(obj, (list, tuple, set, frozenset)):
        return list(obj)
    if hasattr(obj, "__dict__"):
        return list(vars(obj).values())
    return []


def has_cycle(obj) -> bool:
    on_path: set[int] = set()    # ancestrais da busca atual
    done: set[int] = set()       # já explorados sem achar ciclo

    def visit(node) -> bool:
        if isinstance(node, ATOMIC):
            return False
        key = id(node)
        if key in on_path:       # voltamos a um ancestral: ciclo
            return True
        if key in done:          # compartilhado, mas já verificado
            return False
        on_path.add(key)
        found = any(visit(child) for child in _children(node))
        on_path.discard(key)
        done.add(key)
        return found

    return visit(obj)
