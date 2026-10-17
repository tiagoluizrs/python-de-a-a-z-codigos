"""Exercício 2: percorrer dados aninhados (``dict``/``list`` do JSON) de forma ITERATIVA: sem recursão, aguenta qualquer profundidade."""


def depth(data) -> int:
    """A profundidade de ``data``: um valor simples (qualquer coisa que não seja ``dict`` nem ``list``) vale 0; um ``dict`` ou ``list`` vale 1 + a maior
    profundidade dos seus itens (valores, no caso do ``dict``); um contêiner vazio vale 1. Sem recursão: precisa funcionar com 100.000 níveis."""
    raise NotImplementedError


def count_nodes(data) -> int:
    """Quantos nós há: cada ``dict``, cada ``list`` e cada valor simples contam 1 (as CHAVES dos dicts não contam). Sem recursão."""
    raise NotImplementedError


def flatten(data) -> dict:
    """Um dict ``{caminho: valor}`` com um item para cada FOLHA, onde o caminho é uma TUPLA com as chaves e os índices percorridos, e uma folha é um valor
    simples OU um contêiner VAZIO (``{}`` ou ``[]``, guardado como está). O dict resultante segue a ordem de varredura em profundidade, com os dicts na ordem
    de inserção e as listas por índice. ``data`` simples: ``{(): data}``. Sem recursão."""
    raise NotImplementedError


def unflatten(flat: dict):
    """O inverso de ``flatten``: reconstrói a estrutura a partir de ``{caminho: valor}``. Um caminho com um ``int`` no nível seguinte cria uma ``list``
    (índices consecutivos a partir de 0; um buraco ou um início diferente de 0: ``ValueError("índices não consecutivos em ...")`` com o caminho do contêiner);
    um caminho com ``str`` cria um ``dict``; misturar os dois no mesmo contêiner: ``ValueError("chaves misturadas em ...")``. O caminho ``()`` devolve
    o valor direto (e precisa ser o único). Pode usar recursão neste exercício (a profundidade é pequena)."""
    raise NotImplementedError


def find_paths(data, predicate) -> list[tuple]:
    """Os caminhos (tuplas, como em ``flatten``) das folhas em que ``predicate(valor)`` é verdadeiro, na ordem de ``flatten``. Sem recursão."""
    raise NotImplementedError
