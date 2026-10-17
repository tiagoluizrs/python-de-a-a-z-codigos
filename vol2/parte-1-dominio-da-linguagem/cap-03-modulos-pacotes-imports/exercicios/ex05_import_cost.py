"""Exercicio 5: medir o tempo de import e apontar o mais caro.

``most_expensive(modules)`` mede, para cada modulo, o tempo cumulativo
de ``import <modulo>`` em um interpretador novo usando
``python -X importtime`` e devolve ``(nome, microssegundos)`` do mais
caro.

``parse_importtime(stderr, module)`` e a parte testavel: recebe o texto
que o interpretador escreve em stderr e devolve o tempo cumulativo (int,
em microssegundos) da linha cujo ultimo campo e ``module``. As linhas
tem o formato::

    import time: self [us] | cumulative | imported package
    import time:       808 |      13785 | json

Se o modulo nao aparecer, levante ``ValueError``.

Dica: ``line.removeprefix("import time:").split("|")``; o nome pode ter
espacos de indentacao (subimports): use ``strip()``.
"""


def parse_importtime(stderr: str, module: str) -> int:
    raise NotImplementedError


def most_expensive(modules: list[str]) -> tuple[str, int]:
    raise NotImplementedError
