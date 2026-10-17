"""Gabarito do exercício 1."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class EditorMemento:
    _owner: object
    _text: str
    _cursor: int
    _selection: tuple | None


class Editor:
    def __init__(self):
        self.text, self.cursor, self.selection = "", 0, None

    def type(self, chars):
        self.text = self.text[: self.cursor] + chars + self.text[self.cursor:]
        self.cursor += len(chars)
        self.selection = None

    def move(self, pos):
        if not 0 <= pos <= len(self.text):
            raise IndexError(f"posição fora do texto: {pos}")
        self.cursor, self.selection = pos, None

    def select(self, start, end):
        if not 0 <= start <= end <= len(self.text):
            raise ValueError("seleção inválida")
        self.selection, self.cursor = (start, end), end

    def delete_selection(self):
        if self.selection is None:
            raise ValueError("sem seleção")
        start, end = self.selection
        self.text = self.text[:start] + self.text[end:]
        self.cursor, self.selection = start, None

    def save(self):
        return EditorMemento(self, self.text, self.cursor, self.selection)

    def restore(self, memento):
        if not isinstance(memento, EditorMemento):
            raise TypeError("isso não é um memento")
        if memento._owner is not self:
            raise ValueError("memento de outro editor")
        self.text, self.cursor, self.selection = memento._text, memento._cursor, memento._selection


class History:
    def __init__(self, editor, limit=None):
        if limit is not None and limit < 1:
            raise ValueError("limite inválido")
        self.editor = editor
        self._undo = deque(maxlen=limit)
        self._redo = []

    def do(self, action, *args):
        before = self.editor.save()
        try:
            result = action(*args)
        except BaseException:
            self.editor.restore(before)
            raise
        self._undo.append(before)
        self._redo.clear()
        return result

    def undo(self):
        if not self._undo:
            return False
        self._redo.append(self.editor.save())
        self.editor.restore(self._undo.pop())
        return True

    def redo(self):
        if not self._redo:
            return False
        self._undo.append(self.editor.save())
        self.editor.restore(self._redo.pop())
        return True

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)
