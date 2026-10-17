"""Gabarito do exercício 1."""


def _parents(value):
    if value is None:
        return ()
    return (value,) if isinstance(value, str) else tuple(value)


def analyze_revisions(revisions):
    for revision, parent in revisions.items():
        for p in _parents(parent):
            if p not in revisions:
                raise ValueError(f"pai desconhecido: {p!r} (de {revision!r})")
    children = {r: set() for r in revisions}
    for revision, parent in revisions.items():
        for p in _parents(parent):
            children[p].add(revision)
    remaining = {r: set(_parents(parent)) for r, parent in revisions.items()}
    order = []
    ready = sorted(r for r, parents in remaining.items() if not parents)
    while ready:
        current = ready.pop(0)
        order.append(current)
        for child in sorted(children[current]):
            remaining[child].discard(current)
            if not remaining[child] and child not in order and child not in ready:
                ready.append(child)
        ready.sort()
    if len(order) != len(revisions):
        raise ValueError("ciclo no grafo de revisões")
    return {
        "bases": sorted(r for r, parent in revisions.items() if not _parents(parent)),
        "heads": sorted(r for r in revisions if not children[r]),
        "order": order,
    }


def _ancestors(revisions, start):
    seen, stack = set(), [start]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(_parents(revisions[current]))
    return seen


def upgrade_path(revisions, current, target):
    for name in (current, target):
        if name is not None and name not in revisions:
            raise ValueError(f"revisão desconhecida: {name!r}")
    if current == target:
        return []
    already = _ancestors(revisions, current) if current is not None else set()
    wanted = _ancestors(revisions, target)
    order = analyze_revisions(revisions)["order"]
    return [r for r in order if r in wanted and r not in already]
