"""Gabarito do exercicio 6: sombreamento da stdlib."""
import sys
from pathlib import Path


def find_shadowed(folder: Path) -> list[str]:
    found = set()
    for entry in folder.iterdir():
        if entry.name.startswith(("_", ".")):
            continue
        # arquivo x.py ou pasta x: em ambos, o nome do modulo e o 'stem'
        if entry.is_file() and entry.suffix != ".py":
            continue
        name = entry.stem if entry.is_file() else entry.name
        if name in sys.stdlib_module_names:
            found.add(name)
    return sorted(found)
