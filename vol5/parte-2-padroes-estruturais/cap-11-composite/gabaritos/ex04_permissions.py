"""Gabarito do exercício 4."""
from collections import deque


class RoleRegistry:
    def __init__(self):
        self._own: dict[str, set] = {}
        self._includes: dict[str, list] = {}

    def define(self, name, permissions=(), includes=()):
        if name in self._own:
            raise ValueError(f"role já existe: {name}")
        for other in includes:
            if other not in self._own:
                raise ValueError(f"role desconhecida: {other}")
        self._own[name] = set(permissions)
        self._includes[name] = list(includes)

    def _path(self, start, goal):
        """O caminho mais curto de ``start`` até ``goal`` pelos includes (BFS, alfabético), ou None."""
        queue = deque([[start]])
        seen = {start}
        while queue:
            path = queue.popleft()
            if path[-1] == goal:
                return path
            for nxt in sorted(self._includes[path[-1]]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(path + [nxt])
        return None

    def include(self, name, other):
        for role in (name, other):
            if role not in self._own:
                raise KeyError(role)
        back = self._path(other, name)
        if back is not None:
            raise ValueError("ciclo: " + " -> ".join([name] + back))
        if other not in self._includes[name]:
            self._includes[name].append(other)

    def _closure(self, role):
        if role not in self._own:
            raise KeyError(role)
        seen, stack = set(), [role]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self._includes[current])
        return seen

    def permissions(self, role):
        result = set()
        for r in self._closure(role):
            result |= self._own[r]
        return sorted(result)

    def can(self, role, permission):
        return permission in self.permissions(role)

    def explain(self, role, permission):
        if role not in self._own:
            raise KeyError(role)
        queue = deque([[role]])
        seen = {role}
        while queue:
            path = queue.popleft()
            if permission in self._own[path[-1]]:
                return path
            for nxt in sorted(self._includes[path[-1]]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(path + [nxt])
        return None

    def roles_with(self, permission):
        return sorted(r for r in self._own if permission in self.permissions(r))
