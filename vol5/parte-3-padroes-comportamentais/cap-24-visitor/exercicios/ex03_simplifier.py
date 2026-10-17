"""Exercício 3: ``match``/``case``: reescrever árvores de expressões com padrões ANINHADOS (simplificar, derivar, substituir)."""
from dataclasses import dataclass


# ---- (Pronto, NÃO edite.) Os nós ----
@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    left: object
    right: object


@dataclass(frozen=True)
class Mul:
    left: object
    right: object


@dataclass(frozen=True)
class Neg:
    operand: object


def simplify(node):
    """Devolve a árvore simplificada, DE BAIXO PARA CIMA (primeiro os filhos) e REPETINDO até nada mais mudar. As regras:

    * ``0 + x`` e ``x + 0`` viram ``x``; ``1 * x`` e ``x * 1`` viram ``x``; ``0 * x`` e ``x * 0`` viram ``Num(0)``;
    * ``Neg(Neg(x))`` vira ``x``; ``Neg(Num(n))`` vira ``Num(-n)``;
    * ``Num(a) + Num(b)`` vira ``Num(a + b)``; ``Num(a) * Num(b)`` vira ``Num(a * b)``.
    Nada além disso (``x + x`` NÃO vira ``2 * x``). Os nós são imutáveis: devolva nós novos."""
    raise NotImplementedError


def derive(node, var: str):
    """A derivada simbólica em relação a ``var``, já passada por ``simplify``: ``Num`` -> ``Num(0)``; ``Var`` -> ``Num(1)`` se for ``var``, senão ``Num(0)``; ``Add`` -> soma das derivadas;
    ``Mul(a, b)`` -> ``Add(Mul(da, b), Mul(a, db))`` (regra do produto); ``Neg`` -> ``Neg`` da derivada."""
    raise NotImplementedError


def substitute(node, env: dict):
    """Troca cada ``Var`` cujo nome está em ``env`` por ``Num(env[nome])`` (as outras ficam). NÃO simplifica."""
    raise NotImplementedError
