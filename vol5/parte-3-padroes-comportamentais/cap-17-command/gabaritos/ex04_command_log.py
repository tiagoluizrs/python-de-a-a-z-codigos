"""Gabarito do exercício 4."""
import copy
import json


class CommandRegistry:
    def __init__(self):
        self._handlers = {}

    def handler(self, name):
        def register(fn):
            if name in self._handlers:
                raise ValueError(f"comando já registrado: {name}")
            self._handlers[name] = fn
            return fn

        return register

    def _parse(self, command):
        if not isinstance(command, dict) or "name" not in command:
            raise ValueError("comando inválido")
        args = command.get("args", {})
        if not isinstance(args, dict):
            raise ValueError("comando inválido")
        name = command["name"]
        if name not in self._handlers:
            raise KeyError(f"comando desconhecido: {name}")
        return self._handlers[name], args

    def execute(self, state, command):
        fn, args = self._parse(command)
        return fn(state, **args)

    def replay(self, state, log):
        for i, command in enumerate(log):
            fn, args = self._parse(command)
            try:
                state = fn(state, **args)
            except Exception as error:
                raise RuntimeError(f"comando {i} falhou: {error}") from error
        return state


class Journal:
    def __init__(self, registry, state):
        self._registry, self._state, self._log = registry, state, []

    def apply(self, command):
        new_state = self._registry.execute(self._state, command)
        self._state = new_state
        self._log.append(copy.deepcopy(command))

    @property
    def state(self):
        return self._state

    @property
    def log(self):
        return copy.deepcopy(self._log)

    def dumps(self):
        return json.dumps(self._log, sort_keys=True)

    @classmethod
    def loads(cls, registry, initial_state, text):
        journal = cls(registry, initial_state)
        for command in json.loads(text):
            journal.apply(command)
        return journal

    def state_at(self, initial_state, n):
        if not 0 <= n <= len(self._log):
            raise ValueError("n fora do intervalo")
        return self._registry.replay(initial_state, self._log[:n])
