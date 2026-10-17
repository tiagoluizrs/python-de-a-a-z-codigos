"""Gabarito do exercício 3: difflib."""
import difflib


def text_diff(old: str, new: str) -> list[str]:
    return list(difflib.unified_diff(
        old.splitlines(), new.splitlines(), "old", "new", lineterm=""))


def changed_lines(old: str, new: str) -> tuple[list[str], list[str]]:
    removed, added = [], []
    for line in text_diff(old, new):
        # Cabeçalhos começam com "---", "+++" ou "@@"; pule-os
        if line.startswith(("---", "+++", "@@")):
            continue
        if line.startswith("-"):
            removed.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
    return removed, added


def closest(word: str, options: list[str]) -> str | None:
    found = difflib.get_close_matches(word, options, n=1)
    return found[0] if found else None
