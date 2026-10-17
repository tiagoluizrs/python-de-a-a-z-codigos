"""Exercício 5: montar uma wheel de Python puro à mão."""
from pathlib import Path


def build_wheel(dest, name, version, files, entry_points=None, requires=(), requires_python=">=3.9"):
    """Cria ``<dest>/<nome>-<versão>-py3-none-any.whl`` e devolve o ``Path``.

    * ``nome`` no arquivo e na pasta dist-info usa ``_`` no lugar de ``-``/``.``
      (``"my-pkg"`` -> ``my_pkg``); ``name`` nos METADADOS fica como foi dado;
    * ``files``: ``{"pacote/modulo.py": "texto"}`` gravados como estão (UTF-8);
    * pasta ``<nome>-<versão>.dist-info/`` com:
      ``METADATA`` (linhas ``Metadata-Version: 2.1``, ``Name:``, ``Version:``,
      ``Requires-Python:`` e uma ``Requires-Dist:`` por item de ``requires``),
      ``WHEEL`` (``Wheel-Version: 1.0``, ``Generator: manual``,
      ``Root-Is-Purelib: true``, ``Tag: py3-none-any``),
      ``entry_points.txt`` (só se ``entry_points`` for dado: dict
      ``{"console_scripts": {"cmd": "pacote.modulo:funcao"}}`` no formato INI) e
      ``RECORD`` com os hashes de TODOS os outros arquivos (formato do exercício 4);
    * linhas separadas por ``"\\n"``, cada arquivo terminando em ``"\\n"``.

    O resultado deve ser instalável por um instalador de verdade e importável."""
    raise NotImplementedError
