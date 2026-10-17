"""Exercicio 4: carregador de plugins com ``importlib``.

``load_plugins(folder)`` procura arquivos ``*.py`` em ``folder`` (sem
recursao), ignora os que comecam com ``_`` e carrega cada um **sem**
mexer em ``sys.path``. Cada plugin deve definir uma funcao ``register()``
que devolve um dicionario ``{"name": ..., "run": callable}``.

Devolva ``{name: run}`` ordenado pelo nome do arquivo. Plugins que
falharem ao importar ou sem ``register`` devem ser ignorados
(nao derrubam os demais).

Dicas: ``importlib.util.spec_from_file_location``,
``importlib.util.module_from_spec`` e ``spec.loader.exec_module``.
Use um nome de modulo unico (por exemplo ``f"plugin_{stem}"``).
"""
from collections.abc import Callable
from pathlib import Path


def load_plugins(folder: Path) -> dict[str, Callable]:
    raise NotImplementedError
