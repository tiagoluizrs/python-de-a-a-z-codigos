"""Exercício 6: grafo de importações e ciclos."""
from pathlib import Path


def import_graph(src_root, package):
    """Lê todos os ``.py`` de ``src_root/package`` (use ``ast``) e devolve um
    dict ``{modulo: conjunto_de_modulos_internos}``.

    * nomes dos módulos são pontuados: ``"pkg"`` para o ``__init__.py``,
      ``"pkg.core"`` para ``core.py``, ``"pkg.sub"`` para ``sub/__init__.py``;
    * só entram importações DENTRO do pacote (absolutas ``from pkg.core import
      x``, ``import pkg.core``, e relativas ``from .core import x``,
      ``from . import core``, ``from .. import x``);
    * ``from X import nome`` conta como ``X``, EXCETO quando ``X.nome`` é um
      módulo do pacote: aí conta como ``X.nome`` (``from . import core`` em
      ``pkg/__init__.py`` conta como ``pkg.core``);
    * importações dentro de funções contam também.
    """
    raise NotImplementedError


def find_cycle(graph):
    """Devolve UM ciclo como lista de módulos (``["a", "b", "a"]``: começa e
    termina no mesmo) ou ``None`` se não houver ciclo. Pode usar
    ``graphlib`` ou DFS."""
    raise NotImplementedError
