"""Tipagem gradual: Any é um buraco; object é seguro; cast, ignore e narrowing."""
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = """
from typing import Any, cast

def use_any(x: Any) -> int:
    return x.qualquer_coisa.que_nao_existe()          # Any desliga a verificação

def use_object(x: object) -> int:
    return x.qualquer_coisa                            # object não deixa fazer nada sem checar

def narrow(x: int | str | None) -> str:
    if x is None:
        reveal_type(x)
        return "nada"
    if isinstance(x, int):
        reveal_type(x)
        return str(x + 1)
    reveal_type(x)
    return x.upper()

value = cast(int, "texto")                             # cast MENTE: o verificador acredita
reveal_type(value)
bad: int = "x"  # type: ignore[assignment]            # ignora SÓ este código de erro
unused: int = 3  # type: ignore[assignment]            # ignore desnecessário
data = {"a": 1, "b": "dois"}
reveal_type(data)
lst = [1, "a", 2.5]
reveal_type(lst)
"""

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "sample.py"
    path.write_text(SOURCE, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "mypy", "--strict", "--warn-unused-ignores", "--no-incremental",
                             "--cache-dir", folder, str(path)], capture_output=True, text=True, encoding="utf-8")
    for line in result.stdout.splitlines():
        print(line.replace(str(path), "sample.py"))
