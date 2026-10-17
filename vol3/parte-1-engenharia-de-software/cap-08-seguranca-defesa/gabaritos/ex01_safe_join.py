"""Gabarito do exercício 1."""
from pathlib import Path, PureWindowsPath


def safe_join(base, *parts):
    root = Path(base).resolve()
    for part in parts:
        text = str(part)
        if "\0" in text:
            raise ValueError("byte nulo no caminho")
        if Path(text).is_absolute() or PureWindowsPath(text).is_absolute() or PureWindowsPath(text).drive or text.startswith(("/", "\\")):
            raise ValueError(f"caminho absoluto não permitido: {text!r}")
    resolved = root.joinpath(*parts).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"fora da pasta-base: {parts!r}")
    return resolved
