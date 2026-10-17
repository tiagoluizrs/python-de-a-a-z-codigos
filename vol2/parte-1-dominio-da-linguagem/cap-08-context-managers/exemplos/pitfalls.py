"""Armadilhas do with."""
import tempfile
from contextlib import contextmanager
from pathlib import Path

workdir = tempfile.TemporaryDirectory()
path = Path(workdir.name) / "a.txt"
path.write_text("dados")

# 1) O recurso fica fechado depois do with, mas o NOME continua existindo
with open(path) as handle:
    pass
print("handle.closed =", handle.closed)
try:
    handle.read()
except ValueError as error:
    print("ValueError:", error)

# 2) `with` NÃO cria escopo: variáveis do corpo continuam visíveis
with open(path) as handle:
    content = handle.read()
print("content depois do with:", content)

# 3) Retornar True do __exit__ engole QUALQUER exceção que chegue
class Swallow:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return True


with Swallow():
    raise RuntimeError("perdida sem aviso")
print("o erro sumiu: perigoso")


# 4) Se __enter__ falha, __exit__ NÃO roda
class EnterFails:
    def __enter__(self):
        raise OSError("falhou ao abrir")

    def __exit__(self, *exc):
        print("  __exit__ (não deveria aparecer)")


try:
    with EnterFails():
        pass
except OSError as error:
    print("OSError:", error, "(sem __exit__)")


# 5) return dentro do with ainda executa o __exit__
@contextmanager
def noisy():
    print("  entra")
    try:
        yield
    finally:
        print("  sai")


def uses_return():
    with noisy():
        return "retornou"


print(uses_return())

# 6) Instâncias de classe podem ser reutilizadas; geradores não
class Reusable:
    uses = 0

    def __enter__(self):
        Reusable.uses += 1
        return self

    def __exit__(self, *exc):
        return False


manager = Reusable()
with manager:
    pass
with manager:
    pass
print("usos da mesma instância:", Reusable.uses)
workdir.cleanup()
