"""Exercicio 1: criar um pacote com API publica via ``__init__``.

Implemente ``make_package(root, name, modules, public)``.

- Cria a pasta ``root/name`` com um ``__init__.py``.
- ``modules`` mapeia nome de modulo -> codigo-fonte, por exemplo
  ``{"core": "def run(): ...", "_helpers": "def h(): ..."}``.
  Cada item vira o arquivo ``root/name/<modulo>.py``.
- ``public`` mapeia modulo -> lista de nomes a reexportar, por exemplo
  ``{"core": ["run"]}``. O ``__init__.py`` deve conter
  ``from .core import run`` e um ``__all__`` com todos os nomes publicos.

Depois de ``sys.path.insert(0, root)``, ``import name`` deve expor
apenas a API publica em ``__all__``.

Dica: monte as linhas de texto e use ``Path.write_text``.
"""
from pathlib import Path


def make_package(root: Path, name: str, modules: dict[str, str],
                 public: dict[str, list[str]]) -> None:
    raise NotImplementedError
