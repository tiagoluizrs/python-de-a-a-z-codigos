"""Gabarito do exercício 4."""


class StrategyRegistry:
    def __init__(self):
        self._strategies = {}
        self._default = None
        self._rules = []

    def register(self, name, *, default=False):
        def decorator(fn):
            if name in self._strategies:
                raise ValueError(f"estratégia já registrada: {name}")
            if default and self._default is not None:
                raise ValueError(f"já existe um padrão: {self._default}")
            self._strategies[name] = fn
            if default:
                self._default = name
            return fn

        return decorator

    def get(self, name=None):
        if name is None:
            if self._default is None:
                raise LookupError("sem estratégia padrão")
            name = self._default
        try:
            return self._strategies[name]
        except KeyError:
            available = ", ".join(sorted(self._strategies)) or "nenhuma"
            raise KeyError(f"estratégia desconhecida: {name}; disponíveis: {available}") from None

    def names(self):
        return sorted(self._strategies)

    def add_rule(self, predicate, name):
        self.get(name)
        self._rules.append((predicate, name))

    def resolve(self, context):
        for predicate, name in self._rules:
            if predicate(context):
                return self._strategies[name]
        return self.get()

    def run(self, context, *args, **kwargs):
        return self.resolve(context)(*args, **kwargs)
