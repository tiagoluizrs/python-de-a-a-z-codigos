"""Exercício 3: uma árvore de expressões: folhas (``Num``, ``Var``) e composições (``Add``, ``Mul``, ``Neg``) com a MESMA interface."""
from dataclasses import dataclass


class Expr:
    """A interface comum: ``evaluate(env)``, ``variables()``, ``simplify()``, ``__str__`` e a precedência ``prec`` (um inteiro; maior liga mais forte)."""

    prec = 10

    def evaluate(self, env: dict):
        raise NotImplementedError

    def variables(self) -> set:
        raise NotImplementedError

    def simplify(self) -> "Expr":
        raise NotImplementedError


@dataclass(frozen=True)
class Num(Expr):
    """Uma constante. ``evaluate`` devolve o valor; ``variables()`` é vazio; ``simplify()`` é ela mesma; ``str`` é ``repr(valor)`` (``3``, ``2.5``, ``-4``)."""

    value: float

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


@dataclass(frozen=True)
class Var(Expr):
    """Uma variável. ``evaluate`` procura em ``env``; ausente: ``NameError(f"variável indefinida: {nome}")``; ``str`` é o nome."""

    name: str

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


@dataclass(frozen=True)
class Add(Expr):
    """``left + right`` (precedência 1). ``str``: ``"a + b"``; um filho com precedência MENOR que a do pai leva parênteses; no filho DIREITO, a precedência
    IGUAL também (``a + (b + c)``, que é diferente de ``a + b + c`` quando a árvore é agrupada à direita)."""

    left: Expr
    right: Expr
    prec = 1

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        """Simplifica os filhos primeiro; depois: ``Num + Num`` vira ``Num`` (a soma); ``0 + x`` e ``x + 0`` viram ``x``; o resto fica ``Add`` dos filhos simplificados."""
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


@dataclass(frozen=True)
class Mul(Expr):
    """``left * right`` (precedência 2). ``str``: ``"a * b"`` com a mesma regra de parênteses de ``Add``."""

    left: Expr
    right: Expr
    prec = 2

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        """Filhos primeiro; depois: ``Num * Num`` vira ``Num``; ``0 * x`` e ``x * 0`` viram ``Num(0)``; ``1 * x`` e ``x * 1`` viram ``x``; o resto fica ``Mul``."""
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


@dataclass(frozen=True)
class Neg(Expr):
    """``-operand`` (precedência 3). ``str``: ``"-x"``; o filho leva parênteses se a precedência dele for MENOR que 3 (``-(a + b)``)."""

    operand: Expr
    prec = 3

    def evaluate(self, env):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def simplify(self):
        """Filho primeiro; depois: ``-Num(v)`` vira ``Num(-v)``; ``-(-x)`` vira ``x``; o resto fica ``Neg``."""
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError
