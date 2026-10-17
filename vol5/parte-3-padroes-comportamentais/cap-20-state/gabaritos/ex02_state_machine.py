"""Gabarito do exercício 2."""
from collections import deque


class InvalidTransition(Exception):
    pass


def _label(state):
    return getattr(state, "value", None) if hasattr(state, "value") else str(state)


class StateMachine:
    def __init__(self, table, initial):
        states = {s for s, _ in table} | set(table.values())
        if initial not in states:
            raise ValueError(f"estado inicial desconhecido: {initial!r}")
        self._table, self._initial = dict(table), initial
        self._state = initial
        self._history = [initial]
        self._callbacks = []

    @property
    def state(self):
        return self._state

    @property
    def history(self):
        return list(self._history)

    def fire(self, event):
        key = (self._state, event)
        if key not in self._table:
            raise InvalidTransition(f"{event} não permitido em {_label(self._state)}")
        origin, target = self._state, self._table[key]
        self._state = target
        self._history.append(target)
        for callback in self._callbacks:
            callback(origin, event, target)
        return target

    def can(self, event):
        return (self._state, event) in self._table

    def allowed(self):
        return sorted((e for (s, e) in self._table if s == self._state), key=str)

    @property
    def is_terminal(self):
        return not self.allowed()

    def on_transition(self, callback):
        self._callbacks.append(callback)
        return callback

    def reset(self):
        self._state = self._initial
        self._history = [self._initial]


def _graph(table):
    graph = {}
    for (state, event), target in table.items():
        graph.setdefault(state, {})[event] = target
        graph.setdefault(target, {})
    return graph


def _reachable(graph, initial):
    seen, queue = {initial}, deque([initial])
    while queue:
        for target in graph.get(queue.popleft(), {}).values():
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def validate_table(table, initial):
    graph = _graph(table)
    seen = _reachable(graph, initial)
    unreachable = sorted((s for s in graph if s not in seen), key=str)
    terminal = sorted((s for s, out in graph.items() if not out), key=str)
    live_events = {e for (s, e) in table if s in seen}
    dead = sorted({e for (s, e) in table if s not in seen} - live_events, key=str)
    return {"unreachable": unreachable, "terminal": terminal, "dead_events": dead}


def shortest_path(table, start, goal):
    if start == goal:
        return []
    graph = _graph(table)
    queue, seen = deque([(start, [])]), {start}
    while queue:
        state, path = queue.popleft()
        for event in sorted(graph.get(state, {}), key=str):
            target = graph[state][event]
            if target == goal:
                return path + [event]
            if target not in seen:
                seen.add(target)
                queue.append((target, path + [event]))
    return None
