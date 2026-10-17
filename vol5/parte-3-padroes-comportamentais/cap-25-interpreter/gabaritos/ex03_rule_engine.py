"""Gabarito do exercício 3."""
import ast
import operator

BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}
COMPARE = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}


def _not_allowed(node):
    return ValueError(f"expressão não permitida: {type(node).__name__}")


def _build(node, names):
    match node:
        case ast.Constant(value):
            if not (value is None or isinstance(value, (bool, int, float, str))):
                raise _not_allowed(node)
            return lambda ctx: value
        case ast.Name(id=name):
            names.add(name)

            def lookup(ctx):
                if name not in ctx:
                    raise KeyError(f"variável indefinida: {name}")
                return ctx[name]

            return lookup
        case ast.BoolOp(op, values) if isinstance(op, (ast.And, ast.Or)):
            fns = [_build(v, names) for v in values]
            is_and = isinstance(op, ast.And)

            def boolean(ctx):
                result = is_and
                for fn in fns:
                    result = fn(ctx)
                    if bool(result) != is_and:
                        return result
                return result

            return boolean
        case ast.UnaryOp(ast.Not(), operand):
            fn = _build(operand, names)
            return lambda ctx: not fn(ctx)
        case ast.UnaryOp(ast.USub(), operand):
            fn = _build(operand, names)
            return lambda ctx: -fn(ctx)
        case ast.BinOp(left, op, right) if type(op) in BINARY:
            fl, fr, apply = _build(left, names), _build(right, names), BINARY[type(op)]
            return lambda ctx: apply(fl(ctx), fr(ctx))
        case ast.BinOp(_, op, _):
            raise _not_allowed(op)
        case ast.Compare(left, ops, comparators):
            for op in ops:
                if type(op) not in COMPARE:
                    raise _not_allowed(op)
            fl = _build(left, names)
            steps = [(COMPARE[type(op)], _build(c, names)) for op, c in zip(ops, comparators)]

            def compare(ctx):
                current = fl(ctx)
                for apply, fn in steps:
                    right = fn(ctx)
                    if not apply(current, right):
                        return False
                    current = right
                return True

            return compare
        case ast.Tuple(elts) | ast.List(elts):
            fns = [_build(e, names) for e in elts]
            return lambda ctx: tuple(fn(ctx) for fn in fns)
    raise _not_allowed(node)


def compile_expr(expression):
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError:
        raise ValueError("sintaxe inválida") from None
    names = set()
    fn = _build(tree.body, names)
    return fn, frozenset(names)


class Rule:
    def __init__(self, name, expression):
        if not name.strip():
            raise ValueError("nome vazio")
        self.name, self.expression = name, expression
        self._fn, self.variables = compile_expr(expression)

    def matches(self, ctx):
        return bool(self._fn(ctx))


class RuleEngine:
    def __init__(self):
        self._rules = {}

    def add(self, name, expression):
        if name in self._rules:
            raise ValueError(f"regra já existe: {name}")
        rule = Rule(name, expression)
        self._rules[name] = rule
        return rule

    def remove(self, name):
        if name not in self._rules:
            raise LookupError(name)
        del self._rules[name]

    def evaluate(self, ctx):
        matched, errors = [], {}
        for name, rule in self._rules.items():
            missing = sorted(rule.variables - ctx.keys())
            if missing:
                errors[name] = f"variável indefinida: {missing[0]}"
                continue
            try:
                if rule.matches(ctx):
                    matched.append(name)
            except Exception as error:
                errors[name] = f"{type(error).__name__}: {error}"
        return {"matched": matched, "errors": errors}

    def needed_variables(self):
        return frozenset().union(*(r.variables for r in self._rules.values()))

    def __len__(self):
        return len(self._rules)
