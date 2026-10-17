"""Gabarito do exercício 6."""


def _deps(services):
    graph = {}
    for name, options in services.items():
        raw = options.get("depends_on") or []
        deps = list(raw) if not isinstance(raw, dict) else list(raw)
        for dep in deps:
            if dep not in services:
                raise ValueError(f"{name} depende de {dep}, que não existe")
        graph[name] = deps
    return graph


def _find_cycle(graph):
    state = {}

    def visit(node, path):
        state[node] = 1
        for dep in sorted(graph[node]):
            if state.get(dep) == 1:
                cycle = path[path.index(dep):] + [dep]
                smallest = min(cycle[:-1])
                i = cycle.index(smallest)
                body = cycle[:-1][i:] + cycle[:-1][:i]
                return body + [body[0]]
            if dep not in state:
                found = visit(dep, path + [dep])
                if found:
                    return found
        state[node] = 2
        return None

    for node in sorted(graph):
        if node not in state:
            found = visit(node, [node])
            if found:
                return found
    return None


def startup_waves(services):
    graph = _deps(services)
    cycle = _find_cycle(graph)
    if cycle:
        raise ValueError("ciclo: " + " -> ".join(cycle))
    wave_of = {}

    def level(node):
        if node not in wave_of:
            wave_of[node] = 0 if not graph[node] else 1 + max(level(d) for d in graph[node])
        return wave_of[node]

    for node in graph:
        level(node)
    waves = [[] for _ in range(max(wave_of.values(), default=-1) + 1)]
    for node, n in wave_of.items():
        waves[n].append(node)
    return [sorted(w) for w in waves]


def shutdown_order(services):
    return [name for wave in reversed(startup_waves(services)) for name in wave]


def dependents_of(services, name):
    graph = _deps(services)
    if name not in services:
        raise ValueError(f"serviço inexistente: {name}")
    found, frontier = set(), {name}
    while frontier:
        frontier = {n for n, deps in graph.items() if frontier & set(deps)} - found
        found |= frontier
    return sorted(found)
