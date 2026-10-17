"""Gabarito do exercício 3."""


class Store:
    def __init__(self, **initial):
        self._values = dict(initial)
        self._rules = {}              # nome -> (fn, deps)
        self._order = []              # ordem de definição dos derivados (já é topológica: as dependências existem antes)
        self._watchers = {}
        self._log = []

    def _notify(self, name, old, new):
        for callback in self._watchers.get(name, []):
            callback(old, new)

    def set(self, key, value):
        if key in self._rules:
            raise ValueError("derivado não pode ser alterado")
        if key in self._values and self._values[key] == value:
            return
        old = self._values.get(key)
        self._values[key] = value
        changed = {key}
        self._notify(key, old, value)
        for name in self._order:
            fn, deps = self._rules[name]
            if changed.intersection(deps):
                before = self._values[name]
                new = fn(*(self._values[d] for d in deps))
                self._values[name] = new
                self._log.append(name)
                if new != before:
                    changed.add(name)
                    self._notify(name, before, new)

    def derive(self, name, fn, *deps):
        if name in deps:
            raise ValueError("ciclo")
        if name in self._values or name in self._rules:
            raise ValueError(f"já existe: {name}")
        for dep in deps:
            if dep not in self._values:
                raise KeyError(dep)
        self._rules[name] = (fn, deps)
        self._order.append(name)
        self._values[name] = fn(*(self._values[d] for d in deps))

    def get(self, name):
        return self._values[name]

    def __getitem__(self, name):
        return self._values[name]

    def watch(self, name, callback):
        if name not in self._values:
            raise KeyError(name)
        self._watchers.setdefault(name, []).append(callback)
        return callback

    @property
    def recomputed(self):
        return list(self._log)

    def clear_log(self):
        self._log.clear()
