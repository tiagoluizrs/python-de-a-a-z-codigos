"""Gabarito do exercício 3."""
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    fn: object
    deps: list = field(default_factory=list)
    retries: int = 0
    version: str = "1"


def _graph(tasks):
    names = [t.name for t in tasks]
    if len(set(names)) != len(names):
        raise ValueError("nome de tarefa repetido")
    graph = {t.name: list(t.deps) for t in tasks}
    for name, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                raise ValueError(f"{name} depende de {dep}, que não existe")
    return graph


def _find_cycle(graph):
    state = {}

    def visit(node, path):
        state[node] = 1
        for dep in sorted(graph[node]):
            if state.get(dep) == 1:
                cycle = path[path.index(dep):]
                smallest = min(cycle)
                i = cycle.index(smallest)
                body = cycle[i:] + cycle[:i]
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


def execution_order(tasks):
    graph = _graph(tasks)
    cycle = _find_cycle(graph)
    if cycle:
        raise ValueError("ciclo: " + " -> ".join(cycle))
    done, order = set(), []
    while len(order) < len(graph):
        ready = sorted(n for n, deps in graph.items() if n not in done and all(d in done for d in deps))
        order.append(ready[0])
        done.add(ready[0])
    return order


def run(tasks, cache):
    by_name = {t.name: t for t in tasks}
    outputs, keys, log, failed, skipped = {}, {}, [], [], []
    for name in execution_order(tasks):
        task = by_name[name]
        if any(d in failed or d in skipped for d in task.deps):
            skipped.append(name)
            log.append((name, "pulada"))
            continue
        key = (name, task.version, tuple(keys[d] for d in task.deps))
        if key in cache:
            outputs[name], keys[name] = cache[key], key
            log.append((name, "cache"))
            continue
        inputs = [outputs[d] for d in task.deps]
        for attempt in range(task.retries + 1):
            try:
                value = task.fn(*inputs)
                break
            except Exception:
                if attempt == task.retries:
                    value = None
                    failed.append(name)
                    log.append((name, "falhou"))
        else:
            continue
        if name in failed:
            continue
        cache[key] = value
        outputs[name], keys[name] = value, key
        log.append((name, "ok"))
    return {"outputs": outputs, "log": log, "failed": failed, "skipped": skipped}
