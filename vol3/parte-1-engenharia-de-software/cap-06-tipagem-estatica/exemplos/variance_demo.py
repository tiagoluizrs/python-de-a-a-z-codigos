"""Variância: por que list[int] não é list[object], mas Sequence[int] é Sequence[object]."""
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = """
from collections.abc import Callable, Sequence

def total(xs: list[object]) -> int:
    xs.append("intruso")          # list é MUTÁVEL: aceitar list[int] aqui quebraria a lista do chamador
    return len(xs)

def count(xs: Sequence[object]) -> int:
    return len(xs)                # Sequence é só leitura: list[int] é aceita

ints: list[int] = [1, 2]
total(ints)                       # erro: list é invariante
count(ints)                       # ok: Sequence é covariante

def run(callback: Callable[[int], object]) -> None: ...
def takes_object(x: object) -> int: return 1
def takes_bool(x: bool) -> int: return 1
run(takes_object)                 # ok: um aceita-tudo serve (contravariância no parâmetro)
run(takes_bool)                   # erro: exigiria bool, mas run passa int

class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item          # atributo mutável -> invariante
class Frozen[T]:
    def __init__(self, item: T) -> None:
        self._item = item
    def get(self) -> T:
        return self._item         # só leitura -> covariante (inferido!)

b1: Box[object] = Box(1)                    # inferido como Box[object]: ok
b2: Box[int] = Box(1)
b3: Box[object] = b2                        # erro: invariante
f1: Frozen[int] = Frozen(1)
f2: Frozen[object] = f1                     # ok: variância inferida pelo verificador
"""

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "variance.py"
    path.write_text(SOURCE, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "mypy", "--strict", "--no-incremental", "--cache-dir", folder, str(path)],
                            capture_output=True, text=True, encoding="utf-8")
    for line in result.stdout.splitlines():
        text = line.replace(str(path), "variance.py")
        print(text[:150])
