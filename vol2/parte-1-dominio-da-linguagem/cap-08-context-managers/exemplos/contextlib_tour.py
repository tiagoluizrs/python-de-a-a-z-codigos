"""A caixa de ferramentas da contextlib."""
import contextlib
import io
import os
import tempfile
from contextlib import (closing, nullcontext, redirect_stdout, suppress,
                        ContextDecorator)

# suppress: o jeito curto de ignorar uma exceção ESPERADA
with tempfile.TemporaryDirectory() as tmp:
    target = os.path.join(tmp, "nao_existe.txt")
    with suppress(FileNotFoundError):
        os.remove(target)
    print("removido (ou já não existia)")

# closing: para objetos com close() que não são gerenciadores
class Legacy:
    def close(self):
        print("  Legacy.close()")


with closing(Legacy()):
    print("usando Legacy")

# redirect_stdout: captura o que foi impresso
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("isto vai para o buffer")
print("capturado:", repr(buffer.getvalue()))

# chdir (3.11): muda a pasta de trabalho e SEMPRE volta
before = os.getcwd()
with tempfile.TemporaryDirectory() as tmp:
    with contextlib.chdir(tmp):
        print("dentro:", os.path.samefile(os.getcwd(), tmp))
print("voltou:", os.getcwd() == before)

# nullcontext: um `with` opcional sem if/else duplicado
def process(lock=None):
    with lock if lock is not None else nullcontext():
        return "processado"


import threading
print(process(), process(threading.Lock()))

# ContextDecorator: a mesma classe serve de `with` e de decorador
class Announce(ContextDecorator):
    def __enter__(self):
        print("  >>> entrou")
        return self

    def __exit__(self, *exc):
        print("  <<< saiu")
        return False


@Announce()
def work():
    print("  trabalhando")


work()

# AbstractContextManager: documenta a intenção e dá __enter__ pronto
class Quiet(contextlib.AbstractContextManager):
    def __exit__(self, exc_type, exc, tb):
        return False


with Quiet() as q:
    print(type(q).__name__)
