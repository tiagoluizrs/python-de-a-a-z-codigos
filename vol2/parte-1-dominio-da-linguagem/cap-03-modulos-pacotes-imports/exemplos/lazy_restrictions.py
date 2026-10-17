"""Onde 'lazy import' NAO e permitido (erros de sintaxe)."""
CASES = {
    "funcao": "def f():\n    lazy import os\n",
    "classe": "class A:\n    lazy import os\n",
    "try": "try:\n    lazy import os\nexcept ImportError:\n    pass\n",
    "estrela": "lazy from os import *\n",
    "future": "lazy from __future__ import annotations\n",
}
for label, source in CASES.items():
    try:
        compile(source, "<demo>", "exec")
    except SyntaxError as exc:
        print(f"{label:8}", exc.msg)

# 'lazy' continua sendo um nome comum fora de 'lazy import'/'lazy from'
lazy = 3
print(lazy + 1)
