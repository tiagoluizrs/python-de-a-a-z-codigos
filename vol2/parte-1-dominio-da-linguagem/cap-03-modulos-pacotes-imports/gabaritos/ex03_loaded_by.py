"""Gabarito do exercicio 3: modulos carregados por um import."""
import subprocess
import sys

# O codigo roda em um interpretador novo: antes x depois do import.
# 'importlib' e importado ANTES do instantaneo para nao poluir o resultado.
CODE = """
import sys, importlib
before = set(sys.modules)
importlib.import_module({name!r})
for mod in sorted(set(sys.modules) - before):
    print(mod)
"""


def modules_loaded_by(name: str) -> set[str]:
    out = subprocess.run([sys.executable, "-c", CODE.format(name=name)],
                         capture_output=True, text=True, check=True)
    return set(out.stdout.split())
