"""Gabarito do exercício 3."""


def _sources(arg):
    tokens = [t for t in arg.split() if not t.startswith("--")]
    return tokens[:-1]


def _affected(source, changed):
    source = source.rstrip("/")
    if source in (".", ""):
        return bool(changed)
    return any(path == source or path.startswith(source + "/") for path in changed)


def first_invalidated(instructions, changed):
    for index, (kind, arg) in enumerate(instructions):
        if kind.upper() == "COPY" and any(_affected(s, changed) for s in _sources(arg)):
            return index
    return None


def rebuild_cost(instructions, seconds, changed):
    if len(instructions) != len(seconds):
        raise ValueError("instructions e seconds precisam ter o mesmo tamanho")
    first = first_invalidated(instructions, changed)
    return 0.0 if first is None else float(sum(seconds[first:]))


def best_order(instructions, change_frequency):
    result, block = [], []

    def flush():
        block.sort(key=lambda ins: change_frequency.get(_sources(ins[1])[0] if _sources(ins[1]) else "", 1.0))
        result.extend(block)
        block.clear()

    for ins in instructions:
        if ins[0].upper() == "COPY":
            block.append(ins)
        else:
            flush()
            result.append(ins)
    flush()
    return result
