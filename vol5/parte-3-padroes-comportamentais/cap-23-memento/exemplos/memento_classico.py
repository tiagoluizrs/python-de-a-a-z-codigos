"""Memento, forma clássica (GoF): salvar e restaurar o estado de um objeto SEM expor a sua estrutura interna."""
import ast
import copy
import inspect
import textwrap
import time
from dataclasses import dataclass


# --- 1. o problema: desfazer mexendo nas tripas do objeto ---
class NaiveEditor:
    def __init__(self):
        self.text, self.cursor = "", 0

    def type(self, chars):
        self.text = self.text[: self.cursor] + chars + self.text[self.cursor:]
        self.cursor += len(chars)


def naive_undo_stack():
    editor, saved = NaiveEditor(), []
    for chunk in ("olá", ", mundo"):
        saved.append((editor.text, editor.cursor))          # quem salva CONHECE os campos do editor
        editor.type(chunk)
    editor.text, editor.cursor = saved.pop()                # ...e quem restaura também
    return editor.text


print("desfazer pelas tripas:", repr(naive_undo_stack()), "| o código de fora conhece text e cursor: um campo novo (seleção, fonte) quebra o desfazer em silêncio")


# --- 2. o Memento: o originador cria e lê; o zelador só GUARDA ---
@dataclass(frozen=True)
class EditorMemento:
    _owner: object                                          # quem pode restaurar
    _text: str
    _cursor: int


class Editor:
    """Originador: sabe tirar e recolocar o seu próprio estado."""

    def __init__(self):
        self.text, self.cursor = "", 0

    def type(self, chars):
        self.text = self.text[: self.cursor] + chars + self.text[self.cursor:]
        self.cursor += len(chars)

    def save(self):
        return EditorMemento(self, self.text, self.cursor)

    def restore(self, memento):
        if not isinstance(memento, EditorMemento) or memento._owner is not self:
            raise ValueError("memento de outro editor")
        self.text, self.cursor = memento._text, memento._cursor


class History:
    """Zelador: guarda os mementos e NÃO olha dentro deles."""

    def __init__(self, editor):
        self.editor, self._undo, self._redo = editor, [], []

    def do(self, action, *args):
        self._undo.append(self.editor.save())
        self._redo.clear()                                  # uma ação nova apaga o "refazer"
        action(*args)

    def undo(self):
        if self._undo:
            self._redo.append(self.editor.save())
            self.editor.restore(self._undo.pop())

    def redo(self):
        if self._redo:
            self._undo.append(self.editor.save())
            self.editor.restore(self._redo.pop())


editor = Editor()
history = History(editor)
history.do(editor.type, "olá")
history.do(editor.type, ", mundo")
print("\ndepois de digitar:", repr(editor.text))
history.undo()
print("desfazer:", repr(editor.text), "| desfazer de novo:", end=" ")
history.undo()
print(repr(editor.text), "| refazer:", end=" ")
history.redo()
print(repr(editor.text))
history.do(editor.type, "!")
history.redo()
print("ação nova apaga o refazer:", repr(editor.text), "(o refazer não voltou)")

other = Editor()
try:
    other.restore(editor.save())
except ValueError as error:
    print("memento estrangeiro:", error)

# --- 3. a armadilha: o memento que guarda uma REFERÊNCIA (o alias) ---
class ListEditor:
    def __init__(self):
        self.lines = []

    def save(self):
        return list(self.lines)                             # cópia RASA: as linhas internas continuam compartilhadas

    def save_deep(self):
        return copy.deepcopy(self.lines)

    def restore(self, memento):
        self.lines = memento


rich = ListEditor()
rich.lines = [["a"], ["b"]]
shallow, deep = rich.save(), rich.save_deep()
rich.lines[0].append("X")                                   # mexe em uma linha que o memento "guardou"
print("\nmemento raso depois de editar uma linha:", shallow, "(corrompido: ainda aponta para a mesma linha)")
print("memento profundo:", deep, "(intacto)")


# --- 4. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\npelas tripas:", measure([NaiveEditor, naive_undo_stack]), "| Memento (EditorMemento + Editor + History):", measure([EditorMemento, Editor, History]))


def best(fn, n=50_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


e = Editor()
e.type("x" * 1000)
print(f"save() de um editor com 1000 caracteres: {best(e.save):4.0f} ns (a string é imutável: o memento só guarda a REFERÊNCIA)")
