"""Exercicio 3: listar os modulos carregados por um import.

``modules_loaded_by(name)`` devolve o conjunto de nomes que passam a
existir em ``sys.modules`` quando ``import name`` roda, **incluindo o
proprio modulo**, mas sem o que o interpretador ja carrega ao iniciar.

Importante: faca isso em um interpretador novo (``subprocess`` com
``sys.executable``), senao os modulos que voce ja importou nao contam.
O subprocesso deve imprimir os nomes, um por linha.

Dica: rode ``-c`` com um codigo que tira um instantaneo de
``sys.modules`` antes e depois do import.
"""


def modules_loaded_by(name: str) -> set[str]:
    raise NotImplementedError
