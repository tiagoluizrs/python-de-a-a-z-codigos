"""ast: o código como dados."""
import ast
import dis

source = "result = price * (1 + tax) if price > 0 else 0"
tree = ast.parse(source)
print(ast.dump(tree.body[0], indent=1)[:260], "...")


# NodeVisitor: percorrer a árvore
class NameCollector(ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit_Name(self, node):
        self.names.append((node.id, type(node.ctx).__name__))


collector = NameCollector()
collector.visit(tree)
print(collector.names)


# NodeTransformer: reescrever a árvore (ex.: trocar + por *)
class AddToMul(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            node.op = ast.Mult()
        return node


expr = ast.parse("2 + 3 + 4", mode="eval")
new = ast.fix_missing_locations(AddToMul().visit(expr))
print(ast.unparse(new), "=", eval(compile(new, "<ast>", "eval")))

# ast.literal_eval: avaliação SEGURA de literais
print(ast.literal_eval("{'a': [1, 2.5, None, True], 'b': (1, 2)}"))
for dangerous in ("__import__('os').getcwd()", "1 + 2"):
    try:
        ast.literal_eval(dangerous)
    except ValueError as error:
        print("ValueError:", dangerous, "->", str(error)[:40])

# Do texto ao bytecode
code = compile("x + 1", "<demo>", "eval")
dis.dis(code)

# exec: executar texto como código (poderoso e perigoso)
namespace = {}
exec("def double(x):\n    return x * 2", namespace)
print(namespace["double"](21))

# Análise estática simples: quais funções um trecho chama?
class Calls(ast.NodeVisitor):
    def __init__(self):
        self.called = set()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called.add(node.func.attr)
        self.generic_visit(node)


calls = Calls()
calls.visit(ast.parse("print(len(items)); items.append(sum(x))"))
print(sorted(calls.called))
