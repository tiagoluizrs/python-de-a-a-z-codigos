"""Gabarito do exercício 2."""
from pathlib import Path

IGNORED = {"tests", "docs", "build", "dist", "src"}


def _package_dirs(base):
    return [p for p in base.iterdir() if p.is_dir() and (p / "__init__.py").exists()]


def check_layout(root):
    root = Path(root)
    problems = set()
    if not (root / "pyproject.toml").exists():
        problems.add("no-pyproject")
    if not (root / "README.md").exists():
        problems.add("no-readme")
    if not (root / "tests").is_dir():
        problems.add("no-tests")

    src = root / "src"
    if src.is_dir():
        roots = [p for p in src.iterdir() if p.is_dir()]
        for test_file in src.rglob("test_*.py"):
            problems.add("tests-in-package")
    else:
        flat = [p for p in root.iterdir()
                if p.is_dir() and not p.name.startswith(".") and p.name not in IGNORED
                and (p / "__init__.py").exists()]
        if flat:
            problems.add("flat-layout")
        roots = flat
    for package in roots:
        for folder in [package, *[d for d in package.rglob("*") if d.is_dir() and d.name != "__pycache__"]]:
            if any(folder.glob("*.py")) and not (folder / "__init__.py").exists():
                problems.add("missing-init")
    return sorted(problems)
