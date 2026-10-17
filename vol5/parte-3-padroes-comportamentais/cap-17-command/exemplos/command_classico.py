"""Command, forma clássica (GoF): transformar uma AÇÃO em um objeto, que pode ser guardado, repetido e desfeito."""
import ast
import inspect
import textwrap
from abc import ABC, abstractmethod


# --- 1. o problema: chamar métodos direto não deixa rastro, e não há como desfazer ---
class Document:
    def __init__(self, text=""):
        self.text = text


doc = Document("olá")
doc.text = doc.text + ", mundo"                         # alteração direta: nada guarda o que foi feito
print("direto:", doc.text, "| desfazer? o texto antigo se perdeu")


# --- 2. a forma clássica: a interface Command com execute() e undo(), e um objeto por ação ---
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Insert(Command):
    def __init__(self, doc, pos, text):
        self.doc, self.pos, self.text = doc, pos, text

    def execute(self):
        self.doc.text = self.doc.text[:self.pos] + self.text + self.doc.text[self.pos:]

    def undo(self):
        self.doc.text = self.doc.text[:self.pos] + self.doc.text[self.pos + len(self.text):]


class Delete(Command):
    def __init__(self, doc, start, end):
        self.doc, self.start, self.end, self.removed = doc, start, end, ""

    def execute(self):
        self.removed = self.doc.text[self.start:self.end]            # guarda o que removeu: é o que permite DESFAZER
        self.doc.text = self.doc.text[:self.start] + self.doc.text[self.end:]

    def undo(self):
        self.doc.text = self.doc.text[:self.start] + self.removed + self.doc.text[self.start:]


class History:                                                       # o INVOCADOR: executa e guarda
    def __init__(self):
        self.done, self.undone = [], []

    def run(self, command):
        command.execute()
        self.done.append(command)
        self.undone.clear()                                          # uma ação nova invalida o "refazer"

    def undo(self):
        if self.done:
            command = self.done.pop()
            command.undo()
            self.undone.append(command)

    def redo(self):
        if self.undone:
            command = self.undone.pop()
            command.execute()
            self.done.append(command)


doc, history = Document("olá"), History()
history.run(Insert(doc, 3, ", mundo"))
history.run(Delete(doc, 0, 1))
print("\nexecutou duas ações:", repr(doc.text))
history.undo()
print("desfez a última:    ", repr(doc.text))
history.undo()
print("desfez a anterior:  ", repr(doc.text))
history.redo()
print("refez uma:          ", repr(doc.text))
history.run(Insert(doc, 0, "> "))
history.redo()
print("ação nova limpa o 'refazer' (redo não faz nada):", repr(doc.text), "| desfeitas guardadas:", len(history.undone))


# --- 3. o comando composto (macro): vários comandos como um só ---
class Macro(Command):
    def __init__(self, *commands):
        self.commands = commands

    def execute(self):
        for command in self.commands:
            command.execute()

    def undo(self):
        for command in reversed(self.commands):                      # desfaz na ordem INVERSA
            command.undo()


doc, history = Document("abc"), History()
history.run(Macro(Insert(doc, 3, "d"), Insert(doc, 4, "e"), Delete(doc, 0, 1)))
print("\nmacro:", repr(doc.text), "->", end=" ")
history.undo()
print("desfeita de uma vez:", repr(doc.text))


# --- 4. a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nCommand + Insert + Delete + Macro + History:", measure([Command, Insert, Delete, Macro, History]))
