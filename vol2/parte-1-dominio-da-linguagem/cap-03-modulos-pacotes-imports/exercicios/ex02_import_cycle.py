"""Exercicio 2: detectar um import circular.

``find_cycle(graph)`` recebe um grafo de dependencias entre modulos,
``{"a": ["b"], "b": ["c"], "c": []}`` (a importa b, b importa c), e
devolve **um** ciclo como lista de nomes que comeca e termina no mesmo
modulo, por exemplo ``["a", "b", "a"]``. Se nao houver ciclo, devolve
``None``. Modulos citados so como dependencia (sem chave) nao tem
dependencias.

Dica: busca em profundidade guardando o caminho atual (a "pilha").
Se voce encontra um vizinho que ja esta no caminho, achou um ciclo.
"""


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    raise NotImplementedError
