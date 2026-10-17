"""Gabarito do exercício 3."""
from dataclasses import dataclass
from typing import Any, Callable


class InvalidTransition(Exception):
    pass


class GuardFailed(Exception):
    pass


@dataclass(frozen=True)
class Transition:
    target: str
    guard: Callable[[Any], bool] | None = None
    action: Callable[[Any], Any] | None = None


class Machine:
    def __init__(self, transitions, initial, **context):
        self._transitions = dict(transitions)
        self._state = initial
        self._log = []
        self.args = {}
        for name, value in context.items():
            setattr(self, name, value)

    @property
    def state(self):
        return self._state

    @property
    def log(self):
        return list(self._log)

    def fire(self, event, **kwargs):
        key = (self._state, event)
        if key not in self._transitions:
            raise InvalidTransition(f"{event} não permitido em {self._state}")
        transition = self._transitions[key]
        self.args = dict(kwargs)
        if transition.guard is not None and not transition.guard(self):
            raise GuardFailed(f"guarda recusou {event} em {self._state}")
        result = transition.action(self) if transition.action is not None else None
        origin, self._state = self._state, transition.target
        self._log.append((origin, event, self._state))
        return result


def turnstile(price=2, **context):
    def add_credit(m):
        m.credit += m.args["amount"]
        return m.credit

    def push(m):
        m.passed += 1
        m.credit -= m.price
        return "passou"

    def refund(m):
        amount, m.credit = m.credit, 0
        return amount

    def has_credit(m):
        return m.credit > 0

    table = {
        ("locked", "coin"): Transition("unlocked", guard=lambda m: m.args["amount"] >= m.price, action=add_credit),
        ("unlocked", "coin"): Transition("unlocked", action=add_credit),
        ("unlocked", "push"): Transition("locked", action=push),
        ("unlocked", "refund"): Transition("locked", guard=has_credit, action=refund),
        ("locked", "refund"): Transition("locked", guard=has_credit, action=refund),
    }
    return Machine(table, "locked", price=price, credit=0, passed=0, **context)
