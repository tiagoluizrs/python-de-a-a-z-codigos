"""Gabarito do exercício 2."""
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self): ...

    @abstractmethod
    def undo(self): ...


class SetValue(Command):
    _MISSING = object()

    def __init__(self, store, key, value):
        self.store, self.key, self.value, self.old = store, key, value, SetValue._MISSING

    def execute(self):
        self.old = self.store.get(self.key, SetValue._MISSING)
        self.store[self.key] = self.value

    def undo(self):
        if self.old is SetValue._MISSING:
            self.store.pop(self.key, None)
        else:
            self.store[self.key] = self.old


class Fail(Command):
    def __init__(self, message="falhou"):
        self.message, self.undone = message, False

    def execute(self):
        raise RuntimeError(self.message)

    def undo(self):
        self.undone = True


class Macro(Command):
    def __init__(self, *commands):
        self._commands = commands
        self._executed = False

    def execute(self):
        done = []
        try:
            for command in self._commands:
                command.execute()
                done.append(command)
        except BaseException:
            for command in reversed(done):
                try:
                    command.undo()
                except Exception:
                    pass
            raise
        self._executed = True

    def undo(self):
        if not self._executed:
            raise RuntimeError("macro não executada")
        for command in reversed(self._commands):
            command.undo()
        self._executed = False

    def __len__(self):
        return len(self._commands)


def run_all(commands):
    Macro(*commands).execute()
    return list(commands)
