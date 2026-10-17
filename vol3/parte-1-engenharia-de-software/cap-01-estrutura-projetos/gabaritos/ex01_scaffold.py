"""Gabarito do exercício 1."""
import re
from pathlib import Path


def package_name(project_name):
    name = re.sub(r"[-.]", "_", project_name.lower())
    if not name.isidentifier():
        raise ValueError(f"nome inválido: {project_name!r}")
    return name


def create_project(root, project_name):
    pkg = package_name(project_name)
    base = Path(root) / project_name
    base.mkdir(parents=True)                     # FileExistsError se já existir
    files = {
        "pyproject.toml": (
            "[project]\n"
            f'name = "{project_name}"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.15"\n'
            "dependencies = []\n\n"
            "[project.scripts]\n"
            f'{project_name} = "{pkg}.cli:main"\n\n'
            "[build-system]\n"
            'requires = ["uv_build>=0.13.0,<0.14.0"]\n'
            'build-backend = "uv_build"\n'
        ),
        "README.md": f"# {project_name}\n",
        ".gitignore": ".venv/\n__pycache__/\n",
        f"src/{pkg}/__init__.py": "",
        f"src/{pkg}/__main__.py": "from .cli import main\n\nraise SystemExit(main())\n",
        f"src/{pkg}/cli.py": "def main(argv=None):\n    return 0\n",
        "tests/test_smoke.py": f"import {pkg}\n\n\ndef test_import():\n    assert {pkg}\n",
    }
    for relative, content in files.items():
        path = base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return sorted(files)
