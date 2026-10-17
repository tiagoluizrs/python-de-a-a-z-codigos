"""ExitStack: quantidade dinâmica de recursos e limpeza garantida."""
import tempfile
from contextlib import ExitStack
from pathlib import Path


class Resource:
    log = []

    def __init__(self, name, fail=False):
        self.name, self.fail = name, fail

    def __enter__(self):
        if self.fail:
            raise OSError(f"não abriu {self.name}")
        Resource.log.append(f"abre {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        Resource.log.append(f"fecha {self.name}")
        return False


# 1) Quantos arquivos? Só sabemos em tempo de execução
with tempfile.TemporaryDirectory() as tmp:
    paths = []
    for i in range(3):
        path = Path(tmp) / f"f{i}.txt"
        path.write_text(f"conteudo {i}")
        paths.append(path)
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        print([f.read() for f in files])
    print("todos fechados:", all(f.closed for f in files))

# 2) Falha ao abrir o 3º: os dois primeiros são fechados
Resource.log.clear()
try:
    with ExitStack() as stack:
        for name, fail in (("A", False), ("B", False), ("C", True)):
            stack.enter_context(Resource(name, fail))
except OSError as error:
    print("erro:", error)
print(Resource.log)

# 3) callback: registra qualquer função de limpeza (ordem inversa)
with ExitStack() as stack:
    stack.callback(print, "  limpeza 1")
    stack.callback(print, "  limpeza 2")
    print("  corpo")

# 4) pop_all: transfere a posse dos recursos para outro dono
Resource.log.clear()
with ExitStack() as stack:
    stack.enter_context(Resource("X"))
    stack.enter_context(Resource("Y"))
    transferred = stack.pop_all()           # a pilha original fica vazia
print("depois do with:", Resource.log)      # nada foi fechado ainda
transferred.close()
print("depois do close:", Resource.log)
