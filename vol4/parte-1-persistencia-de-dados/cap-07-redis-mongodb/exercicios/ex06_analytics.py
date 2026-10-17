"""Exercício 6: agregações, índices e planos no MongoDB."""


def sales_by_category(collection, min_amount=0):
    """Documentos ``{"category": str, "amount": número}``. Devolve uma lista de tuplas
    ``(categoria, total, quantidade)`` considerando só ``amount >= min_amount``, ordenada pelo total
    decrescente (desempate pela categoria), usando UM ``aggregate`` (``$match``, ``$group``, ``$sort``)."""
    raise NotImplementedError


def top_customers(collection, n=3):
    """Documentos ``{"customer": str, "amount": número}``. Os ``n`` clientes com maior soma:
    lista de ``(cliente, total)`` em ordem decrescente (desempate pelo nome), em UM ``aggregate``
    com ``$limit``. ``n < 1`` levanta ``ValueError``."""
    raise NotImplementedError


def ensure_ttl_index(collection, field, seconds):
    """Cria (se faltar) um índice TTL em ``field`` com ``expireAfterSeconds=seconds``. Devolve
    ``True`` se CRIOU agora, ``False`` se já existia um índice igual. ``seconds < 0`` levanta ``ValueError``."""
    raise NotImplementedError


def winning_stages(collection, query):
    """Lista dos nomes dos estágios do plano vencedor de ``find(query).explain()``, do mais externo para
    o mais interno (siga ``inputStage``), por exemplo ``["FETCH", "IXSCAN"]`` ou ``["COLLSCAN"]``."""
    raise NotImplementedError
