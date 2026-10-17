"""Gabarito do exercício 3."""
import fnmatch
from pathlib import Path

DEFAULT_EXCLUDES = ("__pycache__", ".git", ".venv", "dist", "build", ".pytest_cache")


def collect_files(root, include=("**/*",), exclude=()):
    root = Path(root)
    selected = set()
    for pattern in include:
        for path in root.glob(pattern):
            if path.is_file():
                selected.add(path.relative_to(root).as_posix())
    result = []
    for relative in selected:
        parts = relative.split("/")
        if any(part in DEFAULT_EXCLUDES for part in parts[:-1]) or relative.endswith(".pyc"):
            continue
        if any(fnmatch.fnmatch(relative, pattern) for pattern in exclude):
            continue
        result.append(relative)
    return sorted(result)
