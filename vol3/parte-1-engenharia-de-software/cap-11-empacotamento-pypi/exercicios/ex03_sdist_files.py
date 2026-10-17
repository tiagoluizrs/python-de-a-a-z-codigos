"""Exercício 3: quais arquivos entram na sdist."""
from pathlib import Path

DEFAULT_EXCLUDES = ("__pycache__", ".git", ".venv", "dist", "build", ".pytest_cache")


def collect_files(root, include=("**/*",), exclude=()):
    """Devolve a lista ORDENADA de caminhos relativos (com ``/``) dos ARQUIVOS de
    ``root`` que entram na sdist.

    * ``include``: padrões ``Path.glob`` (relativos a ``root``); um arquivo entra
      se casar com ALGUM;
    * ``exclude``: padrões ``fnmatch`` aplicados ao caminho relativo
      (``"tests/*"``, ``"*.log"``); se casar com algum, sai;
    * SEMPRE saem arquivos que tenham, no caminho, uma pasta de
      ``DEFAULT_EXCLUDES`` e arquivos ``*.pyc``;
    * diretórios não entram (só arquivos)."""
    raise NotImplementedError
