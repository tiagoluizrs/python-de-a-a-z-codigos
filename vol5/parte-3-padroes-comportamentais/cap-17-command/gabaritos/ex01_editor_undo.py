"""Gabarito do exercício 1."""
from abc import ABC, abstractmethod
from collections import deque


class Editor:
    def __init__(self, text=""):
        self.text = text


class Command(ABC):
    @abstractmethod
    def execute(self): ...

    @abstractmethod
    def undo(self): ...


class Insert(Command):
    def __init__(self, editor, pos, text):
        self.editor, self.pos, self.text = editor, pos, text

    def execute(self):
        if not 0 <= self.pos <= len(self.editor.text):
            raise ValueError(f"posição inválida: {self.pos}")
        self.editor.text = self.editor.text[:self.pos] + self.text + self.editor.text[self.pos:]

    def undo(self):
        self.editor.text = self.editor.text[:self.pos] + self.editor.text[self.pos + len(self.text):]


class Delete(Command):
    def __init__(self, editor, start, end):
        self.editor, self.start, self.end, self.removed = editor, start, end, ""

    def execute(self):
        if not 0 <= self.start <= self.end <= len(self.editor.text):
            raise ValueError(f"intervalo inválido: {self.start}-{self.end}")
        self.removed = self.editor.text[self.start:self.end]
        self.editor.text = self.editor.text[:self.start] + self.editor.text[self.end:]

    def undo(self):
        self.editor.text = self.editor.text[:self.start] + self.removed + self.editor.text[self.start:]


class History:
    def __init__(self, limit=None):
        if limit is not None and limit < 1:
            raise ValueError("limit deve ser >= 1")
        self._done = deque(maxlen=limit)
        self._undone = []

    def run(self, command):
        command.execute()
        self._done.append(command)
        self._undone.clear()

    def undo(self):
        if not self._done:
            return False
        command = self._done.pop()
        command.undo()
        self._undone.append(command)
        return True

    def redo(self):
        if not self._undone:
            return False
        command = self._undone.pop()
        command.execute()
        self._done.append(command)
        return True

    @property
    def can_undo(self):
        return bool(self._done)

    @property
    def can_redo(self):
        return bool(self._undone)

    def __len__(self):
        return len(self._done)
