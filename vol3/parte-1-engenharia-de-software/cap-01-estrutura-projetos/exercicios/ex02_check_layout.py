"""Exercício 2: um verificador de layout de projeto."""
from pathlib import Path


def check_layout(root):
    """Devolve a lista ORDENADA de problemas (códigos) do projeto em ``root``.

    Códigos:

    * ``"no-pyproject"``: não existe ``pyproject.toml``;
    * ``"no-readme"``: não existe ``README.md``;
    * ``"no-tests"``: não existe a pasta ``tests``;
    * ``"flat-layout"``: há uma pasta com ``__init__.py`` diretamente na
      raiz e NÃO existe a pasta ``src`` (ignore ``tests``, ``docs``, ``build``,
      ``dist`` e pastas que começam com ``.``);
    * ``"missing-init"``: dentro de ``src/<pacote>`` (ou do pacote plano), uma
      subpasta que contém ``.py`` mas não tem ``__init__.py``;
    * ``"tests-in-package"``: existe um arquivo ``test_*.py`` dentro de
      ``src/``.

    Projeto correto devolve ``[]``.
    """
    raise NotImplementedError
