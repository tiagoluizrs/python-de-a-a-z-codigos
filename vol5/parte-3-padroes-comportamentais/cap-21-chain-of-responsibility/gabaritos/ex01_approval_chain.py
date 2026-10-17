"""Gabarito do exercício 1."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    amount: float
    description: str
    category: str = "geral"


class Handler(ABC):
    name = "handler"

    def __init__(self):
        self._next = None

    def set_next(self, handler):
        node = handler
        while node is not None:
            if node is self:
                raise ValueError("ciclo na cadeia")
            node = node._next
        self._next = handler
        return handler

    def _walk(self):
        node = self
        while node is not None:
            yield node
            node = node._next

    def handle(self, expense):
        for node in self._walk():
            if node.can_handle(expense):
                return node.process(expense)
        return None

    def trace(self, expense):
        visited = []
        for node in self._walk():
            visited.append(node.name)
            if node.can_handle(expense):
                break
        return visited

    @abstractmethod
    def can_handle(self, expense): ...

    @abstractmethod
    def process(self, expense): ...


class Approver(Handler):
    def __init__(self, role, limit):
        super().__init__()
        self.name, self.role, self.limit = role, role, limit

    def can_handle(self, expense):
        return expense.amount <= self.limit

    def process(self, expense):
        return f"{self.role} aprovou {expense.description}"


class CategoryApprover(Handler):
    def __init__(self, role, category):
        super().__init__()
        self.name, self.role, self.category = role, role, category

    def can_handle(self, expense):
        return expense.category == self.category

    def process(self, expense):
        return f"{self.role} aprovou {expense.description} ({expense.category})"


def build_chain(*handlers):
    if not handlers:
        raise ValueError("cadeia vazia")
    for current, nxt in zip(handlers, handlers[1:]):
        current.set_next(nxt)
    return handlers[0]
