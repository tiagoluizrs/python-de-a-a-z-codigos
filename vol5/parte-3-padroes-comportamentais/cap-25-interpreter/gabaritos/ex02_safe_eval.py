"""Gabarito do exercício 2."""
import ast
import operator

ALLOWED = {
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.UAdd,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    ast.Tuple, ast.List, ast.Set,
}
BINARY = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow,
}
COMPARE = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}


def _validate(tree):
    for node in ast.walk(tree):
        if type(node) not in ALLOWED:
            raise ValueError(f"expressão não permitida: {type(node).__name__}")
        if isinstance(node, ast.Constant) and not (node.value is None or isinstance(node.value, (bool, int, float, str))):
            raise ValueError("expressão não permitida: Constant")


def _is_number(value):
    return isinstance(value, (int, float))                       # bool é int


def _eval(node, ctx):
    match node:
        case ast.Constant(value):
            return value
        case ast.Name(id=name):
            if name not in ctx:
                raise KeyError(f"variável indefinida: {name}")
            return ctx[name]
        case ast.BoolOp(ast.And(), values):
            result = True
            for value in values:
                result = _eval(value, ctx)
                if not result:
                    return result
            return result
        case ast.BoolOp(ast.Or(), values):
            result = False
            for value in values:
                result = _eval(value, ctx)
                if result:
                    return result
            return result
        case ast.UnaryOp(ast.Not(), operand):
            return not _eval(operand, ctx)
        case ast.UnaryOp(op, operand):
            value = _eval(operand, ctx)
            if not _is_number(value):
                raise ValueError("operandos devem ser números")
            return -value if isinstance(op, ast.USub) else +value
        case ast.BinOp(left, op, right):
            a, b = _eval(left, ctx), _eval(right, ctx)
            if not (_is_number(a) and _is_number(b)):
                raise ValueError("operandos devem ser números")
            if isinstance(op, ast.Pow) and abs(b) > 100:
                raise ValueError("expoente grande demais")
            return BINARY[type(op)](a, b)
        case ast.Compare(left, ops, comparators):
            current = _eval(left, ctx)
            for op, right_node in zip(ops, comparators):
                right = _eval(right_node, ctx)
                if not COMPARE[type(op)](current, right):
                    return False
                current = right
            return True
        case ast.Tuple(elts):
            return tuple(_eval(e, ctx) for e in elts)
        case ast.List(elts):
            return [_eval(e, ctx) for e in elts]
        case ast.Set(elts):
            return {_eval(e, ctx) for e in elts}
    raise ValueError(f"expressão não permitida: {type(node).__name__}")


def safe_eval(expression, ctx=None):
    if len(expression) > 1_000:
        raise ValueError("expressão grande demais")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError:
        raise ValueError("sintaxe inválida") from None
    _validate(tree)
    return _eval(tree.body, ctx or {})
