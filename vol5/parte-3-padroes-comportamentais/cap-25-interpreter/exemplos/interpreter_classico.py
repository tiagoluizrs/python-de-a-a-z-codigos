"""Interpreter, forma clássica (GoF): a gramática de uma linguagem pequena vira uma hierarquia de classes, e cada classe sabe se interpretar."""
import ast
import inspect
import re
import textwrap
import time

# Gramática (cada regra vira uma classe e um método do analisador):
#   expr       := and_expr ("or" and_expr)*
#   and_expr   := not_expr ("and" not_expr)*
#   not_expr   := "not" not_expr | comparison
#   comparison := value (("==" | "!=" | "<" | "<=" | ">" | ">=") value)?
#   value      := NUMBER | STRING | NAME | "(" expr ")"


# --- 1. o problema: regras de negócio escritas por quem NÃO programa ---
def naive_rule(user):
    return user["age"] >= 18 and (user["country"] == "BR" or user["vip"])        # uma função Python: o analista precisa de um programador


print("regra escrita como código:", naive_rule({"age": 20, "country": "BR", "vip": False}), "| para o analista de negócio mudar '18' para '21', alguém precisa editar, testar e publicar o programa")


# --- 2. o Interpreter: uma classe por regra da gramática ---
class Expression:
    def interpret(self, ctx):
        raise NotImplementedError


class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def interpret(self, ctx):
        return self.value


class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def interpret(self, ctx):
        if self.name not in ctx:
            raise KeyError(f"variável indefinida: {self.name}")
        return ctx[self.name]


class Compare(Expression):
    OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}

    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right

    def interpret(self, ctx):
        return self.OPS[self.op](self.left.interpret(ctx), self.right.interpret(ctx))


class And(Expression):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def interpret(self, ctx):
        return bool(self.left.interpret(ctx)) and bool(self.right.interpret(ctx))      # curto-circuito


class Or(Expression):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def interpret(self, ctx):
        return bool(self.left.interpret(ctx)) or bool(self.right.interpret(ctx))


class Not(Expression):
    def __init__(self, operand):
        self.operand = operand

    def interpret(self, ctx):
        return not self.operand.interpret(ctx)


# a árvore montada à mão (é o que o analisador produz a partir do TEXTO):
tree = And(Compare(">=", Variable("age"), Literal(18)), Or(Compare("==", Variable("country"), Literal("BR")), Variable("vip")))
print("\nárvore montada à mão:", tree.interpret({"age": 20, "country": "BR", "vip": False}), tree.interpret({"age": 17, "country": "BR", "vip": False}))


# --- 3. o analisador (parser): do TEXTO à árvore ---
TOKEN = re.compile(r"""\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<str>'[^']*'|"[^"]*")|(?P<op><=|>=|==|!=|<|>|\(|\))|(?P<name>[A-Za-z_]\w*))""")
RESERVED = {"and", "or", "not"}


def tokenize(text):
    text, pos, tokens = text.rstrip(), 0, []
    while pos < len(text):
        match = TOKEN.match(text, pos)
        if not match:
            bad = len(text) - len(text[pos:].lstrip())                              # pula os espaços até o caractere problemático
            raise SyntaxError(f"caractere inesperado na posição {bad}: {text[bad]!r}")
        pos = match.end()
        tokens.append((match.lastgroup, match.group(match.lastgroup)))
    return tokens


class Parser:
    def __init__(self, text):
        self.tokens, self.i = tokenize(text), 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def take(self):
        token = self.peek()
        self.i += 1
        return token

    def parse(self):
        node = self.or_expr()
        if self.i < len(self.tokens):
            raise SyntaxError(f"sobrou texto: {self.peek()[1]!r}")
        return node

    def or_expr(self):
        node = self.and_expr()
        while self.peek() == ("name", "or"):
            self.take()
            node = Or(node, self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.peek() == ("name", "and"):
            self.take()
            node = And(node, self.not_expr())
        return node

    def not_expr(self):
        if self.peek() == ("name", "not"):
            self.take()
            return Not(self.not_expr())
        return self.comparison()

    def comparison(self):
        left = self.value()
        kind, text = self.peek()
        if kind == "op" and text in Compare.OPS:
            self.take()
            return Compare(text, left, self.value())
        return left

    def value(self):
        kind, text = self.take()
        if kind == "num":
            return Literal(float(text) if "." in text else int(text))
        if kind == "str":
            return Literal(text[1:-1])
        if kind == "name" and text not in RESERVED:
            return Literal(text == "true") if text in ("true", "false") else Variable(text)
        if (kind, text) == ("op", "("):
            node = self.or_expr()
            if self.take() != ("op", ")"):
                raise SyntaxError("faltou fechar o parêntese")
            return node
        raise SyntaxError(f"esperava um valor, veio {text!r}")


def parse(text):
    return Parser(text).parse()


rule = parse("age >= 18 and (country == 'BR' or vip) and not banned")
ctx = {"age": 20, "country": "PT", "vip": True, "banned": False}
print("\nregra em TEXTO:", rule.interpret(ctx), "|", rule.interpret({**ctx, "banned": True}), "| a regra é um dado: vem de um arquivo, de um banco, de um formulário")

for broken in ("age >=", "age >= 18 )", "age @ 3"):
    try:
        parse(broken)
    except SyntaxError as error:
        print(f"  {broken!r:16} -> SyntaxError: {error}")
try:
    parse("idade > 18").interpret({})
except KeyError as error:
    print("  variável que não existe  ->", error)

# --- 4. a armadilha: reinventar a linguagem inteira ---
print("\nadicionar 'in' (country in ('BR', 'PT')) exige: um token novo, uma regra de gramática, uma classe e uma mudança no analisador; cada recurso é código a manter, testar e documentar")


# --- 5. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) if not isinstance(o, str) else o for o in objects)
    tree_ = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree_))}


print("\nclasses de expressão (Expression + 6):", measure([Expression, Literal, Variable, Compare, And, Or, Not]), "| analisador (tokenize + Parser):", measure([tokenize, Parser, parse]))


def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"analisar a regra (texto -> árvore): {best(lambda: parse('age >= 18 and (country == \"BR\" or vip) and not banned'), 5_000):6.1f} µs | interpretar a árvore pronta: {best(lambda: rule.interpret(ctx)):5.2f} µs")
