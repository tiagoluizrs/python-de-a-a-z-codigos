"""Ler a configuração no import prende o valor: leia sob demanda."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BAD = """
import os
DEBUG = os.environ["APP_DEBUG"]          # lido UMA vez, no import (e quebra se faltar)
def is_debug():
    return DEBUG
"""
GOOD = """
import os
def is_debug():
    return os.environ.get("APP_DEBUG", "0") == "1"      # lido a cada uso
"""

for label, source in (("no import", BAD), ("sob demanda", GOOD)):
    with tempfile.TemporaryDirectory() as folder:
        Path(folder, "settings_mod.py").write_text(source, encoding="utf-8")
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]);\n"
                "os.environ['APP_DEBUG'] = '0'\n"
                "import settings_mod\n"
                "os.environ['APP_DEBUG'] = '1'\n"
                "print(settings_mod.is_debug())")
        result = subprocess.run([sys.executable, "-c", code, folder], capture_output=True, text=True)
        print(f"{label:<12} depois de mudar a variável para 1, is_debug() ->", result.stdout.strip() or result.stderr.strip().splitlines()[-1])

    code_missing = "import sys; sys.path.insert(0, sys.argv[1]); import settings_mod"
    env = {k: v for k, v in os.environ.items() if k != "APP_DEBUG"}
    with tempfile.TemporaryDirectory() as folder:
        Path(folder, "settings_mod.py").write_text(source, encoding="utf-8")
        result = subprocess.run([sys.executable, "-c", code_missing, folder], capture_output=True, text=True, env=env)
        print(f"{label:<12} sem a variável, só importar o módulo ->", "ok" if result.returncode == 0 else result.stderr.strip().splitlines()[-1])
