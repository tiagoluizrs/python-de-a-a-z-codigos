"""Exercício 2: consultas com select() (m é um objeto com Customer, Order e OrderLine)."""


def top_customers(session, m, n=3):
    """Os ``n`` clientes que mais gastaram: lista de tuplas ``(nome, total)`` em ordem decrescente
    do total (``Decimal``), desempate pelo nome. Use ``join``, ``group_by`` e ``func.sum`` (uma
    consulta); clientes sem pedidos NÃO aparecem. ``n < 1`` levanta ``ValueError``."""
    raise NotImplementedError


def orders_with_lines(session, m, customer_id):
    """Pedidos do cliente (por ``id``) com as linhas JÁ carregadas (``selectinload``), de modo
    que percorrer ``order.lines`` NÃO gere consultas extras (no máximo 2 consultas no total)."""
    raise NotImplementedError


def search_customers(session, m, name_contains=None, limit=20, offset=0):
    """Clientes cujo nome contém ``name_contains`` (ignorando maiúsculas; ``%`` e ``_`` do
    usuário são LITERAIS: use ``Customer.name.icontains(texto, autoescape=True)``), ordenados
    por ``id``, paginados. ``limit`` de 1 a 100 e ``offset >= 0`` (senão ``ValueError``)."""
    raise NotImplementedError
