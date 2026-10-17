"""Exercício 1: o Visitor clássico (dupla despacho): os nós só sabem ``accept``; cada operação é uma classe visitante."""
from collections import Counter


# ---- (Pronto, NÃO edite.) A hierarquia de nós ----
class Node:
    def accept(self, visitor):
        raise NotImplementedError


class Num(Node):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_num(self)


class Var(Node):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_var(self)


class Add(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def accept(self, visitor):
        return visitor.visit_add(self)


class Mul(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def accept(self, visitor):
        return visitor.visit_mul(self)


class Neg(Node):
    def __init__(self, operand):
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_neg(self)


# ---- Os visitantes: implemente os cinco métodos ``visit_num``, ``visit_var``, ``visit_add``, ``visit_mul`` e ``visit_neg`` de cada um ----
class Evaluator:
    """``Evaluator(env)``: ``node.accept(Evaluator({"x": 4}))`` calcula o valor da expressão. Variável fora do ``env``: ``KeyError(f"variável indefinida: {name}")``."""

    def __init__(self, env: dict):
        raise NotImplementedError


class Printer:
    """Devolve o texto com o MÍNIMO de parênteses. Precedências: soma 1, produto 2, negação 3, átomos (número e variável) 4.
    A soma NUNCA põe parênteses nos filhos; o produto põe nos filhos que sejam somas; a negação põe nos filhos que sejam somas ou produtos.
    Formato: ``"a + b"``, ``"a * b"``, ``"-a"`` (sem espaço depois do sinal), números com ``str(valor)``.
    Exemplos: ``Mul(Add(Var("x"), Num(3)), Num(2))`` -> ``"(x + 3) * 2"``; ``Neg(Add(x, 1))`` -> ``"-(x + 1)"``; ``Add(Num(2), Mul(x, y))`` -> ``"2 + x * y"``."""


class VariableCollector:
    """Devolve a lista ORDENADA, sem repetições, dos nomes de variáveis da expressão (``[]`` se não há)."""


class Depth:
    """Devolve a profundidade da árvore: número e variável valem ``1``; negação vale ``1 + `` o operando; soma e produto valem ``1 + max(filhos)``."""


class CountVisitor:
    """Um visitante COM ESTADO: os métodos devolvem ``None`` e acumulam em ``self.counts`` (um ``collections.Counter``) quantos nós de cada tipo foram visitados, com os nomes
    ``"Num"``, ``"Var"``, ``"Add"``, ``"Mul"`` e ``"Neg"``. Visitar uma árvore soma os contadores dela aos que já existiam (o mesmo visitante pode visitar várias árvores)."""

    def __init__(self):
        self.counts = Counter()
