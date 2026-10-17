"""Gabarito do exercício 1."""
import re


class Expression:
    def interpret(self, ctx):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError


class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def interpret(self, ctx):
        return self.value

    def variables(self):
        return frozenset()


class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def interpret(self, ctx):
        if self.name not in ctx:
            raise KeyError(f"variável indefinida: {self.name}")
        return ctx[self.name]

    def variables(self):
        return frozenset({self.name})


class Compare(Expression):
    OPS = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }

    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right

    def interpret(self, ctx):
        a, b = self.left.interpret(ctx), self.right.interpret(ctx)
        try:
            return self.OPS[self.op](a, b)
        except TypeError:
            raise TypeError(f"não comparável: {a!r} {self.op} {b!r}") from None

    def variables(self):
        return self.left.variables() | self.right.variables()


class And(Expression):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def interpret(self, ctx):
        return bool(self.left.interpret(ctx)) and bool(self.right.interpret(ctx))

    def variables(self):
        return self.left.variables() | self.right.variables()


class Or(Expression):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def interpret(self, ctx):
        return bool(self.left.interpret(ctx)) or bool(self.right.interpret(ctx))

    def variables(self):
        return self.left.variables() | self.right.variables()


class Not(Expression):
    def __init__(self, operand):
        self.operand = operand

    def interpret(self, ctx):
        return not self.operand.interpret(ctx)

    def variables(self):
        return self.operand.variables()


TOKEN = re.compile(r"""\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<str>'[^']*'|"[^"]*")|(?P<op><=|>=|==|!=|<|>|\(|\))|(?P<name>[A-Za-z_]\w*))""")
RESERVED = {"and", "or", "not"}


def tokenize(text):
    text, pos, tokens = text.rstrip(), 0, []
    while pos < len(text):
        match = TOKEN.match(text, pos)
        if not match:
            bad = len(text) - len(text[pos:].lstrip())
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
