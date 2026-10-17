"""Gabarito do exercício 3."""
from collections import deque
from typing import Protocol, runtime_checkable


@runtime_checkable
class Snapshottable(Protocol):
    def snapshot(self): ...

    def restore(self, snapshot) -> None: ...


class UndoManager:
    def __init__(self, target, limit=50):
        if not isinstance(target, Snapshottable):
            raise TypeError("alvo sem snapshot/restore")
        if limit < 1:
            raise ValueError("limite inválido")
        self.target = target
        self._undo = deque(maxlen=limit)
        self._redo = []

    def checkpoint(self, label=None):
        self._undo.append((label, self.target.snapshot()))
        self._redo.clear()

    def undo(self):
        if not self._undo:
            raise LookupError("nada para desfazer")
        label, snap = self._undo.pop()
        self._redo.append((label, self.target.snapshot()))
        self.target.restore(snap)
        return label

    def redo(self):
        if not self._redo:
            raise LookupError("nada para refazer")
        label, snap = self._redo.pop()
        self._undo.append((label, self.target.snapshot()))
        self.target.restore(snap)
        return label

    def goto(self, label):
        if label not in self.labels():
            raise LookupError(f"checkpoint desconhecido: {label}")
        steps = 0
        while True:
            undone = self.undo()
            steps += 1
            if undone == label:
                return steps

    def labels(self):
        return [label for label, _ in self._undo]

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)
