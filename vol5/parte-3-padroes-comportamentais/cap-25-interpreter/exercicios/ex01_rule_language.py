"""Exercício 1: o Interpreter clássico: cada regra da gramática é uma classe que sabe se interpretar (o analisador já vem pronto)."""
import re

# Gramática:
#   expr       := and_expr ("or" and_expr)*
#   and_expr   := not_expr ("and" not_expr)*
#   not_expr   := "not" not_expr | comparison
#   comparison := value (("==" | "!=" | "<" | "<=" | ">" | ">=") value)?
#   value      := NUMBER | STRING | NAME | "(" expr ")"       (NAME pode ser ``true`` ou ``false``)


class Expression:
    """A base. ``interpret(ctx)`` calcula o valor com as variáveis do dicionário ``ctx``; ``variables()`` devolve um ``frozenset`` com os NOMES de variáveis usados na expressão
    (``frozenset()`` se não há)."""

    def interpret(self, ctx: dict):
        raise NotImplementedError

    def variables(self) -> frozenset:
        raise NotImplementedError


class Literal(Expression):
    """``Literal(value)``: devolve ``value``; não usa variáveis."""

    def __init__(self, value):
        raise NotImplementedError


class Variable(Expression):
    """``Variable(name)``: devolve ``ctx[name]``; fora do ``ctx``: ``KeyError(f"variável indefinida: {name}")``; ``variables()`` é ``{name}``."""

    def __init__(self, name: str):
        raise NotImplementedError


class Compare(Expression):
    """``Compare(op, left, right)``. O atributo de CLASSE ``OPS`` é um dicionário ``{"==": ..., "!=": ..., "<": ..., "<=": ..., ">": ..., ">=": ...}`` de funções de dois argumentos
    (o analisador usa ``text in Compare.OPS``). Tipos que não se comparam (``"a" < 1``): ``TypeError(f"não comparável: {a!r} {op} {b!r}")`` (com os valores calculados)."""

    OPS: dict = {}

    def __init__(self, op: str, left: Expression, right: Expression):
        raise NotImplementedError


class And(Expression):
    """``And(left, right)``: devolve um ``bool``. Com CURTO-CIRCUITO: se a esquerda é falsa, a direita NÃO é calculada (uma variável indefinida à direita não levanta erro)."""

    def __init__(self, left: Expression, right: Expression):
        raise NotImplementedError


class Or(Expression):
    """``Or(left, right)``: devolve um ``bool``, com curto-circuito (se a esquerda é verdadeira, a direita NÃO é calculada)."""

    def __init__(self, left: Expression, right: Expression):
        raise NotImplementedError


class Not(Expression):
    """``Not(operand)``: devolve ``not`` do valor do operando (um ``bool``)."""

    def __init__(self, operand: Expression):
        raise NotImplementedError


# ---- (Pronto, NÃO edite.) O analisador: do texto à árvore ----
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


def parse(text: str) -> Expression:
    return Parser(text).parse()
