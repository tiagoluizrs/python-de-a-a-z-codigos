"""Gabarito do exercício 2."""


def _children(node):
    if isinstance(node, dict):
        return list(node.items())
    if isinstance(node, list):
        return list(enumerate(node))
    return None


def depth(data):
    best = 0
    stack = [(data, 0)]
    while stack:
        node, level = stack.pop()
        kids = _children(node)
        if kids is None:
            best = max(best, level)
        else:
            best = max(best, level + 1)
            stack.extend((value, level + 1) for _, value in kids)
    return best


def count_nodes(data):
    total = 0
    stack = [data]
    while stack:
        node = stack.pop()
        total += 1
        kids = _children(node)
        if kids:
            stack.extend(value for _, value in kids)
    return total


def flatten(data):
    out = {}
    stack = [((), data)]
    while stack:
        path, node = stack.pop()
        kids = _children(node)
        if not kids:
            out[path] = node
        else:
            stack.extend((path + (key,), value) for key, value in reversed(kids))
    return out


def unflatten(flat):
    if () in flat:
        if len(flat) != 1:
            raise ValueError("o caminho () precisa ser o único")
        return flat[()]
    return _build({path: value for path, value in flat.items()}, ())


def _build(flat, prefix):
    groups = {}
    for path, value in flat.items():
        groups.setdefault(path[len(prefix)], {})[path] = value
    keys = list(groups)
    where = "/".join(map(str, prefix)) or "raiz"
    ints = [k for k in keys if isinstance(k, int)]
    if ints and len(ints) != len(keys):
        raise ValueError(f"chaves misturadas em {where}")
    if ints:
        if sorted(ints) != list(range(len(ints))):
            raise ValueError(f"índices não consecutivos em {where}")
        keys = sorted(keys)

    def build_one(key):
        group = groups[key]
        child_prefix = prefix + (key,)
        if child_prefix in group:
            return group[child_prefix]
        return _build(group, child_prefix)

    if ints:
        return [build_one(k) for k in keys]
    return {k: build_one(k) for k in keys}


def find_paths(data, predicate):
    return [path for path, value in flatten(data).items() if predicate(value)]
