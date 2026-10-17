"""Teste de mutação à mão: quem testa os testes? (usa ast, Capítulo 16 do Volume 2)"""
import ast
import types

SOURCE = """
def can_vote(age):
    if age >= 16:
        return True
    return False

def total(prices, discount):
    return sum(prices) - discount
"""


class Mutator(ast.NodeTransformer):
    """Produz UM mutante por vez: troca o n-ésimo operador mutável."""

    SWAPS = {ast.GtE: ast.Gt, ast.Gt: ast.GtE, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Eq: ast.NotEq,
             ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div}

    def __init__(self, target):
        self.target, self.count, self.description = target, -1, None

    def _swap(self, node, attr, items):
        for index, op in enumerate(items):
            if type(op) in self.SWAPS:
                self.count += 1
                if self.count == self.target:
                    new = self.SWAPS[type(op)]()
                    self.description = f"linha {node.lineno}: {type(op).__name__} -> {type(new).__name__}"
                    items[index] = new

    def visit_Compare(self, node):
        self._swap(node, "ops", node.ops)
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        holder = [node.op]
        self._swap(node, "op", holder)
        node.op = holder[0]
        return node


def mutants(source):
    index = 0
    while True:
        tree = ast.parse(source)
        mutator = Mutator(index)
        mutator.visit(tree)
        if mutator.description is None:
            return
        yield mutator.description, compile(ast.fix_missing_locations(tree), "<mutante>", "exec")
        index += 1


def run_suite(code, tests):
    module = types.ModuleType("m")
    exec(code, module.__dict__)
    try:
        for test in tests:
            test(module)
    except AssertionError:
        return False                              # algum teste falhou: o mutante foi "morto"
    return True


def weak(m):
    assert m.can_vote(30) is True                 # nunca testa a fronteira
    assert m.total([10, 20], 5) == 25


def strong(m):
    assert m.can_vote(16) is True and m.can_vote(15) is False and m.can_vote(30) is True
    assert m.total([10, 20], 5) == 25 and m.total([1], 0) == 1 and m.total([], 3) == -3


for name, suite in [("fraca", [weak]), ("forte", [strong])]:
    survived = [desc for desc, code in mutants(SOURCE) if run_suite(code, suite)]
    total = sum(1 for _ in mutants(SOURCE))
    print(f"suíte {name}: {total - len(survived)}/{total} mutantes mortos", "| sobreviveram:", survived)
