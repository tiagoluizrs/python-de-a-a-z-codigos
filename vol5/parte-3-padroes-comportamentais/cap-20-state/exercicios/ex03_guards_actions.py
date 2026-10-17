"""Exercício 3: transições com GUARDAS (condições) e AÇÕES (efeitos): uma catraca de metrô que cobra passagem."""
from dataclasses import dataclass, field
from typing import Any, Callable


class InvalidTransition(Exception):
    pass


class GuardFailed(Exception):
    """A transição existe, mas a guarda recusou."""


@dataclass(frozen=True)
class Transition:
    """``target``: o estado de destino; ``guard``: ``guard(machine) -> bool`` opcional; ``action``: ``action(machine) -> Any`` opcional (o valor devolvido vira o resultado de ``fire``)."""

    target: str
    guard: Callable[[Any], bool] | None = None
    action: Callable[[Any], Any] | None = None


class Machine:
    """``Machine(transitions, initial, **context)``: ``transitions`` é ``{(estado, evento): Transition}``; ``context`` são atributos da máquina (``machine.credit = 0`` etc.) que
    as guardas e ações leem e alteram.

    * ``state``; ``fire(event, **kwargs)``:
        1. sem transição para ``(estado, evento)``: ``InvalidTransition(f"{event} não permitido em {estado}")``;
        2. se há ``guard`` e ``guard(machine)`` é falso: ``GuardFailed(f"guarda recusou {event} em {estado}")`` e o estado NÃO muda (e a ação NÃO roda);
        3. senão, os ``kwargs`` são guardados em ``machine.args`` (um dict) ANTES de chamar a guarda; executa a ``action`` (se houver) ANTES de trocar de estado; se ela levantar
           exceção, o estado NÃO muda; troca para ``target`` e devolve o resultado da ação (``None`` sem ação);
    * ``log``: lista (cópia) de ``(origem, evento, destino)`` das transições feitas."""

    def __init__(self, transitions: dict, initial: str, **context):
        raise NotImplementedError

    @property
    def state(self) -> str:
        raise NotImplementedError

    @property
    def log(self) -> list:
        raise NotImplementedError

    def fire(self, event: str, **kwargs):
        raise NotImplementedError


def turnstile(price: int = 2, **context) -> Machine:
    """A catraca: estados ``"locked"`` (inicial) e ``"unlocked"``; atributos da máquina ``price``, ``credit`` (começa em 0) e ``passed`` (começa em 0); ``context`` extra
    também vira atributo. As transições (``kwargs`` de ``fire`` ficam em ``machine.args``):

    * ``("locked", "coin")`` -> ``unlocked``, com GUARDA ``args["amount"] >= price`` (uma moeda que não paga a passagem inteira é recusada: ``GuardFailed``) e AÇÃO que soma
      ``amount`` a ``credit`` e devolve o novo ``credit``;
    * ``("unlocked", "coin")`` -> ``unlocked``, sem guarda; a ação soma ``amount`` a ``credit`` e devolve o novo ``credit``;
    * ``("unlocked", "push")`` -> ``locked``; a ação faz ``passed += 1`` e ``credit -= price`` e devolve ``"passou"``; em ``locked`` não há ``push`` (``InvalidTransition``);
    * ``("unlocked", "refund")`` e ``("locked", "refund")`` -> ``locked``, com GUARDA ``credit > 0``; a ação devolve o ``credit`` que havia e o zera."""
    raise NotImplementedError
