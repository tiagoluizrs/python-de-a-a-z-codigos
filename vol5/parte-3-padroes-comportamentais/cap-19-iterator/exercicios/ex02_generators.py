"""Exercício 2: geradores (``yield``) para as operações clássicas sobre fluxos, sempre PREGUIÇOSAS (não leem mais do que precisam)."""


def chunks(iterable, size: int):
    """Devolve um iterador de LISTAS de ``size`` itens (a última pode ser menor). ``size < 1``: ``ValueError("size deve ser >= 1")`` levantado NA CHAMADA da função (não só
    no primeiro ``next``). Preguiçoso: só consome do iterável o que cada lista precisa."""
    raise NotImplementedError


def sliding_window(iterable, n: int):
    """Devolve um iterador de TUPLAS com as janelas de ``n`` itens consecutivos: ``sliding_window("abcd", 2)`` -> ``("a","b")``, ``("b","c")``, ``("c","d")``; menos de ``n``
    itens: nenhuma janela. ``n < 1``: ``ValueError("n deve ser >= 1")`` na chamada. Use ``collections.deque(maxlen=n)``."""
    raise NotImplementedError


def unique_everseen(iterable, key=None):
    """Produz cada item na PRIMEIRA vez que aparece (mantém a ordem), considerando iguais os que têm a mesma ``key(item)`` (``key=None``: o próprio item). As chaves precisam ser
    hashable. Preguiçoso."""
    raise NotImplementedError


def merge_sorted(*iterables):
    """Funde iteráveis JÁ ORDENADOS em um único fluxo ordenado, de forma preguiçosa (guarda só o primeiro item de cada iterável). Empates: o item do iterável que veio PRIMEIRO
    nos argumentos sai antes. NÃO use ``heapq.merge``: use ``heapq`` com tuplas ``(valor, indice_do_iteravel, iterador)`` ou equivalente. Sem iteráveis: não produz nada."""
    raise NotImplementedError


def flatten(nested, levels: int | None = None):
    """Achata listas e tuplas aninhadas SEM recursão (pilha explícita), na ordem: ``flatten([1, [2, (3, 4)], 5])`` -> ``1, 2, 3, 4, 5``. ``str`` e ``bytes`` NÃO são abertos
    (contam como itens). ``levels``: quantos níveis abrir (``None`` = todos; ``0`` = nenhum: produz os itens do primeiro nível como estão; ``1`` = abre só o primeiro nível
    de aninhamento). Funciona com aninhamento de 5.000 níveis."""
    raise NotImplementedError


def read_blocks(stream, size: int):
    """Produz blocos de ``size`` (``stream.read(size)``) até o fim (quando ``read`` devolve vazio), usando ``iter(callable, sentinela)``; o sentinela é ``""`` para fluxos de TEXTO (``isinstance(stream, io.TextIOBase)``) e ``b""`` para os demais; devolva o iterador (``size`` é validado na chamada). ``size < 1``:
    ``ValueError("size deve ser >= 1")``. O ``stream`` não é fechado."""
    raise NotImplementedError
