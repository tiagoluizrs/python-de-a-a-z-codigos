"""Exercicio 6: detectar sombreamento de modulos da biblioteca padrao.

``find_shadowed(folder)`` devolve a lista ORDENADA de nomes de modulos
da biblioteca padrao que sao sombreados por algo em ``folder`` (sem
recursao): um arquivo ``nome.py`` ou uma pasta ``nome`` (pacote ou
namespace) cujo nome esteja em ``sys.stdlib_module_names``.

Exemplo: pasta com ``random.py``, ``utils.py`` e ``json/`` devolve
``["json", "random"]``.

Ignore nomes que comecam com ``_`` ou ``.`` e arquivos que nao sejam
``.py`` (um ``email.txt`` nao sombreia nada).
"""
from pathlib import Path


def find_shadowed(folder: Path) -> list[str]:
    raise NotImplementedError
