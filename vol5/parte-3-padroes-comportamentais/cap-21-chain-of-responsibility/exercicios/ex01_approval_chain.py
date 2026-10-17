"""Exercício 1: a Chain of Responsibility clássica: manipuladores encadeados, cada um conhecendo o próximo."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    amount: float
    description: str
    category: str = "geral"


class Handler(ABC):
    """O manipulador base. ``set_next(handler)`` guarda o próximo e o DEVOLVE (para encadear ``a.set_next(b).set_next(c)``); ``handle(expense) -> str | None``:

    * se ``can_handle(expense)``, devolve ``process(expense)``;
    * senão, repassa ao próximo (se houver) e devolve o que ele devolver; sem próximo, devolve ``None``;
    * ``trace(expense) -> list[str]``: os ``name`` de TODOS os manipuladores pelos quais o pedido PASSA até ser resolvido (inclusive o que resolveu) ou até o fim da cadeia, na ordem
      (um pedido que ninguém resolve devolve a lista de todos);
    * a cadeia NÃO deve usar recursão em ``handle`` nem em ``trace`` (percorra a cadeia com um laço ``while``): cadeias de 5.000 manipuladores precisam funcionar;
    * ``set_next`` que criaria um CICLO (o manipulador já está na cadeia de quem recebe, ou é o próprio): ``ValueError("ciclo na cadeia")``;
    * ``name`` (atributo de texto)."""

    name = "handler"

    def __init__(self):
        raise NotImplementedError

    def set_next(self, handler: "Handler") -> "Handler":
        raise NotImplementedError

    def handle(self, expense: Expense):
        raise NotImplementedError

    def trace(self, expense: Expense) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, expense: Expense) -> bool: ...

    @abstractmethod
    def process(self, expense: Expense) -> str: ...


class Approver(Handler):
    """``Approver(role, limit)``: ``name`` é ``role``; ``can_handle`` é ``expense.amount <= limit``; ``process`` devolve ``f"{role} aprovou {descricao}"``."""

    def __init__(self, role: str, limit: float):
        raise NotImplementedError

    def can_handle(self, expense: Expense) -> bool:
        raise NotImplementedError

    def process(self, expense: Expense) -> str:
        raise NotImplementedError


class CategoryApprover(Handler):
    """``CategoryApprover(role, category)``: ``name`` é ``role``; só trata despesas dessa ``category`` (qualquer valor); ``process`` devolve ``f"{role} aprovou {descricao} ({categoria})"``."""

    def __init__(self, role: str, category: str):
        raise NotImplementedError

    def can_handle(self, expense: Expense) -> bool:
        raise NotImplementedError

    def process(self, expense: Expense) -> str:
        raise NotImplementedError


def build_chain(*handlers: Handler) -> Handler:
    """Encadeia os manipuladores na ordem dada e devolve o PRIMEIRO. Sem manipuladores: ``ValueError("cadeia vazia")``. (Use ``set_next``.)"""
    raise NotImplementedError
