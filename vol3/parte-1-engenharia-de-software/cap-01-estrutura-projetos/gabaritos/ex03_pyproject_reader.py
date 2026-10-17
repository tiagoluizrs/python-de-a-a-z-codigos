"""Gabarito do exercício 3."""
import tomllib
from pathlib import Path


def read_project(path):
    with open(Path(path), "rb") as handle:
        data = tomllib.load(handle)
    project = data.get("project")
    if not project or "name" not in project:
        raise ValueError("pyproject.toml sem [project].name")
    return {
        "name": project["name"],
        "version": project.get("version"),
        "requires_python": project.get("requires-python"),
        "dependencies": list(project.get("dependencies", [])),
        "scripts": dict(project.get("scripts", {})),
        "build_backend": data.get("build-system", {}).get("build-backend"),
        "groups": {name: list(items) for name, items in data.get("dependency-groups", {}).items()},
    }
