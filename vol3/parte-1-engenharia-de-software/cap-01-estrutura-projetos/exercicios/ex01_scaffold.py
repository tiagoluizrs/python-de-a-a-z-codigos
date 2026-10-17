"""Exercício 1: gerar o esqueleto de um projeto com layout src."""
from pathlib import Path


def package_name(project_name):
    """Nome de import a partir do nome do projeto: minúsculas, ``-`` e ``.``
    viram ``_``; ``"My-App.Tool"`` -> ``"my_app_tool"``. Se não for um
    identificador válido, levanta ``ValueError``."""
    raise NotImplementedError


def create_project(root, project_name):
    """Cria, dentro de ``root`` (``Path``), a pasta ``project_name`` com:

    * ``pyproject.toml`` válido para ``tomllib`` com ``[project]`` (``name``,
      ``version = "0.1.0"``, ``requires-python = ">=3.15"``,
      ``dependencies = []``), ``[project.scripts]`` (``<project_name> =
      "<pkg>.cli:main"``) e ``[build-system]`` com ``uv_build``;
    * ``README.md`` (começa com ``# <project_name>``);
    * ``.gitignore`` contendo ``.venv/`` e ``__pycache__/``;
    * ``src/<pkg>/__init__.py``, ``src/<pkg>/__main__.py`` e
      ``src/<pkg>/cli.py`` (com ``def main(argv=None): return 0``);
    * ``tests/test_smoke.py`` (importa ``<pkg>``).

    Devolve a lista ORDENADA dos caminhos criados (relativos à pasta do
    projeto, com ``/``). Se a pasta do projeto já existir, ``FileExistsError``.
    """
    raise NotImplementedError
