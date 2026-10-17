"""Duck typing: o que importa é o que o objeto FAZ, não o que ele É."""
import io
import os
import pathlib


def read_first_line(source):
    """Aceita QUALQUER objeto com .readline() (arquivo, StringIO, socket...)."""
    return source.readline().rstrip("\n")


class Clipboard:
    """Nunca ouviu falar de arquivos, mas "grasna" como um."""

    def __init__(self, text):
        self.lines = text.splitlines(keepends=True)

    def readline(self):
        return self.lines.pop(0) if self.lines else ""


print(read_first_line(io.StringIO("do StringIO\nresto")))
print(read_first_line(Clipboard("da área de transferência\nresto")))
try:
    read_first_line(42)
except AttributeError as error:
    print("AttributeError:", error)


# O contrário: checar tipos demais rejeita objetos perfeitamente bons
def open_strict(path):
    if not isinstance(path, str):
        raise TypeError("path deve ser str")
    return os.fspath(path)


def open_duck(path):
    return os.fspath(path)                      # aceita qualquer "path-like"


home = pathlib.PurePosixPath("/srv/app")
try:
    open_strict(home)
except TypeError as error:
    print("estrito:", error)
print("duck   :", open_duck(home), "|", open_duck("/tmp/x"))


# Três formas de lidar com a incerteza
class Dog:
    def speak(self):
        return "au"


class Rock:
    pass


for animal in (Dog(), Rock()):
    # 1) EAFP: tenta e trata (o estilo do Python, Capítulo 7)
    try:
        print("EAFP :", animal.speak())
    except AttributeError:
        print("EAFP : sem speak()")
    # 2) hasattr: pergunta antes (LBYL), vale para casos simples
    print("hasattr:", animal.speak() if hasattr(animal, "speak") else "sem speak()")
    # 3) getattr com padrão
    print("getattr:", getattr(animal, "speak", lambda: "sem speak()")())
