"""Gabarito do exercicio 1: pacote com API publica."""
from pathlib import Path


def make_package(root: Path, name: str, modules: dict[str, str],
                 public: dict[str, list[str]]) -> None:
    package = root / name
    package.mkdir(parents=True, exist_ok=True)

    # Cada modulo vira um arquivo .py
    for module, source in modules.items():
        (package / f"{module}.py").write_text(source, encoding="utf-8")

    # O __init__ reexporta so o que e publico e declara __all__
    lines = []
    exported = []
    for module, names in public.items():
        lines.append(f"from .{module} import {', '.join(names)}")
        exported.extend(names)
    lines.append(f"__all__ = {exported!r}")
    (package / "__init__.py").write_text("\n".join(lines) + "\n",
                                         encoding="utf-8")
