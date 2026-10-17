"""Visitor, forma clássica (GoF): acrescentar operações a uma hierarquia de objetos SEM editar as classes (dupla despacho)."""
import ast
import inspect
import textwrap
import time


# --- 1. o problema: cada operação nova edita TODAS as classes ---
class NaiveNum:
    def __init__(self, value):
        self.value = value

    def evaluate(self, env):
        return self.value

    def show(self):
        return str(self.value)


class NaiveAdd:
    def __init__(self, left, right):
        self.left, self.right = left, right

    def evaluate(self, env):
        return self.left.evaluate(env) + self.right.evaluate(env)

    def show(self):
        return f"({self.left.show()} + {self.right.show()})"


tree = NaiveAdd(NaiveNum(2), NaiveAdd(NaiveNum(3), NaiveNum(4)))
print("operações dentro das classes:", tree.evaluate({}), tree.show(), "| uma operação nova (contar nós, simplificar, exportar) edita CADA classe da hierarquia")


# --- 2. o Visitor: a operação vira uma classe, e as classes só sabem "aceitar" ---
class Node:
    def accept(self, visitor):
        raise NotImplementedError


class Num(Node):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_num(self)                      # 1ª despacho: o tipo do NÓ escolhe o método...


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


class Evaluator:
    def __init__(self, env):
        self.env = env

    def visit_num(self, node):
        return node.value

    def visit_var(self, node):
        return self.env[node.name]

    def visit_add(self, node):
        return node.left.accept(self) + node.right.accept(self)    # 2ª despacho: o tipo do VISITANTE escolhe o código

    def visit_mul(self, node):
        return node.left.accept(self) * node.right.accept(self)


class Printer:
    def visit_num(self, node):
        return str(node.value)

    def visit_var(self, node):
        return node.name

    def visit_add(self, node):
        return f"({node.left.accept(self)} + {node.right.accept(self)})"

    def visit_mul(self, node):
        return f"{node.left.accept(self)} * {node.right.accept(self)}"


expr = Add(Num(2), Mul(Var("x"), Num(5)))
print("\nEvaluator:", expr.accept(Evaluator({"x": 4})), "| Printer:", expr.accept(Printer()))


class Depth:                                                # uma operação NOVA: nenhuma classe de nó foi editada
    def visit_num(self, node):
        return 1

    visit_var = visit_num

    def visit_add(self, node):
        return 1 + max(node.left.accept(self), node.right.accept(self))

    visit_mul = visit_add


print("operação nova sem editar os nós (profundidade):", expr.accept(Depth()))


# --- 3. o problema da expressão (expression problem): o outro lado da moeda ---
class Pow(Node):                                            # um TIPO novo de nó
    def __init__(self, base, exponent):
        self.base, self.exponent = base, exponent

    def accept(self, visitor):
        return visitor.visit_pow(self)


try:
    Pow(Num(2), Num(3)).accept(Evaluator({}))
except AttributeError as error:
    print("\ntipo novo de nó:", error, "| acrescentar um tipo edita TODOS os visitantes, e o esquecimento só aparece em tempo de execução")


# --- 4. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree_ = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree_))}


print("\nnós + 1 operação (Evaluator):", measure([Node, Num, Var, Add, Mul, Evaluator]), "| cada operação a mais custa uma classe de ~10 linhas")


def build(depth):
    if depth == 0:
        return Num(1)
    left, right = build(depth - 1), build(depth - 1)
    return Add(left, right) if depth % 2 else Mul(left, right)


big = build(9)                                              # 1.023 nós
evaluator = Evaluator({})


def best(fn, n=300):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"avaliar uma árvore de 1.023 nós: {best(lambda: big.accept(evaluator)):6.0f} µs ({best(lambda: big.accept(evaluator)) * 1000 / 1023:.0f} ns por nó)")
