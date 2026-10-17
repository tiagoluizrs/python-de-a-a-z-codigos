"""Exercício 2: estratégias de ordenação (funções ``item -> chave``) e como combiná-las."""


def by_attr(name: str, descending: bool = False):
    """Uma estratégia de CHAVE: ``key(item)`` devolve ``item[name]`` se o item é um ``dict`` ou ``getattr(item, name)`` caso contrário; com ``descending=True``
    a chave vale ``-valor`` (só para números). Devolve um objeto com ``.key`` (a função) e ``.descending`` (o ``bool``): use um ``types.SimpleNamespace`` ou uma
    tupla nomeada. Valor ausente: o ``KeyError``/``AttributeError`` normal."""
    raise NotImplementedError


def rank(items, *strategies, reverse: bool = False) -> list:
    """Ordena ``items`` por TODAS as estratégias em sequência (a primeira é a principal, as outras desempatam), respeitando o ``descending`` de cada uma, e devolve
    uma lista nova (os ``items`` originais não mudam). ``reverse=True`` inverte o resultado final. Sem estratégias: a ordem original (cópia). Use UMA chamada a
    ``sorted`` com uma chave que devolve uma tupla (``-valor`` para descendente numérico) ou ordenações estáveis em ordem inversa das estratégias."""
    raise NotImplementedError


def top_n(items, strategy, n: int) -> list:
    """Os ``n`` primeiros de ``items`` pela estratégia (``descending`` respeitado); ``n < 0``: ``ValueError("n negativo")``; ``n`` maior que o total devolve tudo.
    Deve usar ``heapq.nsmallest`` (ou ``nlargest``) em vez de ordenar a lista inteira."""
    raise NotImplementedError


def weighted(**weights):
    """Uma estratégia de chave: soma ponderada dos campos dos itens (dicts): ``weighted(price=-1, rating=2)`` -> ``key(item) = -1 * price + 2 * rating``; a ordenação é
    DESCENDENTE (maior pontuação primeiro). Devolve o mesmo tipo de objeto de ``by_attr`` (com ``.key`` e ``.descending=True``). Campo ausente no item: ``KeyError``.
    Sem pesos: ``ValueError("sem pesos")``."""
    raise NotImplementedError
