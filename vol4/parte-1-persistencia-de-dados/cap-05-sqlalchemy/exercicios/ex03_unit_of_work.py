"""Exercício 3: Repository e Unit of Work (m é um objeto com Customer, Order e OrderLine)."""


class CustomerRepository:
    """``CustomerRepository(session, m)``: ``add(name, email)`` -> ``Customer`` (faz ``flush``,
    NÃO confirma); ``get(id)``; ``get_by_email(email)``; ``all()`` (por ``id``)."""

    def __init__(self, session, m):
        raise NotImplementedError


class OrderRepository:
    """``OrderRepository(session, m)``: ``add(customer, lines)`` com ``lines`` uma lista de
    tuplas ``(produto, quantidade, preço)`` -> ``Order`` (``flush``, não confirma);
    ``for_customer(customer_id)`` -> pedidos com as linhas carregadas (``selectinload``)."""

    def __init__(self, session, m):
        raise NotImplementedError


class UnitOfWork:
    """``UnitOfWork(session_factory, m)`` como gerenciador de contexto:

    * ``__enter__`` cria a sessão e os repositórios ``self.customers`` e ``self.orders``;
    * ``commit()`` confirma; ``rollback()`` desfaz;
    * ``__exit__`` SEMPRE faz ``rollback()`` do que não foi confirmado e fecha a sessão;
      se houve exceção, ela sobe (devolva ``False``);
    * sem ``commit()`` explícito, NADA é gravado."""

    def __init__(self, session_factory, m):
        raise NotImplementedError
