"""Evoluir sem quebrar: avisos de depreciação que apontam para o CHAMADOR."""
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

LIB = """
import warnings
from warnings import deprecated

@deprecated("use new_function(); esta será removida na 3.0")
def old_function():
    return 1

def new_function():
    return 1

def old_name(x):
    warnings.warn("old_name() foi renomeada para new_name()", DeprecationWarning, stacklevel=2)
    return new_function()

def __getattr__(name):                     # PEP 562: atributos de módulo que sumiram
    if name == "OLD_CONSTANT":
        warnings.warn("OLD_CONSTANT mudou para NEW_CONSTANT", DeprecationWarning, stacklevel=2)
        return 42
    raise AttributeError(name)
"""

APP = """
import lib
lib.old_function()          # linha 3
lib.old_name(1)             # linha 4
print(lib.OLD_CONSTANT)     # linha 5
"""

MIDDLE = """
import lib

def use():
    return lib.old_name(1)   # o chamador é UM MÓDULO (não o __main__)
"""

APP_VIA_MIDDLE = """
import middle
middle.use()
print("terminou")
"""


def run(*flags, app="app.py"):
    with tempfile.TemporaryDirectory() as folder:
        Path(folder, "lib.py").write_text(LIB, encoding="utf-8")
        Path(folder, "app.py").write_text(APP, encoding="utf-8")
        Path(folder, "middle.py").write_text(MIDDLE, encoding="utf-8")
        Path(folder, "app_middle.py").write_text(APP_VIA_MIDDLE, encoding="utf-8")
        result = subprocess.run([sys.executable, *flags, app], capture_output=True, text=True, cwd=folder, encoding="utf-8")
        return result


print("--- sem filtros, chamado direto de app.py (__main__): o aviso aparece ---")
result = run()
print("avisos:", result.stderr.count("DeprecationWarning"), "| stdout:", result.stdout.strip())
print("--- sem filtros, chamado por OUTRO módulo (middle.py): o aviso é IGNORADO por padrão ---")
result = run(app="app_middle.py")
print("avisos:", result.stderr.count("DeprecationWarning"), "| stdout:", result.stdout.strip())

print("--- com -W default::DeprecationWarning ---")
for line in run("-W", "default::DeprecationWarning").stderr.splitlines():
    if "Warning" in line:
        print(" ", line.strip())

print("--- com -W error (a suíte de testes de quem usa pode fazer isso) ---")
result = run("-W", "error::DeprecationWarning")
print("  ", result.stderr.strip().splitlines()[-1])

# stacklevel: onde o aviso APONTA
def helper_with_level(level):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        def library():
            warnings.warn("obsoleto", DeprecationWarning, stacklevel=level)

        library()
    return caught[0].filename.split("\\")[-1], caught[0].lineno


print("stacklevel=1 aponta para a própria biblioteca:", helper_with_level(1))
print("stacklevel=2 aponta para quem CHAMOU:", helper_with_level(2))
