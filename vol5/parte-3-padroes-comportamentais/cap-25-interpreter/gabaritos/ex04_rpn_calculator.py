"""Gabarito do exercício 4."""
import operator

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "//": operator.floordiv, "%": operator.mod, "**": operator.pow, "max": max, "min": min}
UNARY = {"neg": operator.neg, "abs": abs}
STACK_NEEDS = {"dup": 1, "swap": 2, "drop": 1, "over": 2}


def _number(token):
    for kind in (int, float):
        try:
            return True, kind(token)
        except ValueError:
            pass
    return False, None


def _run(text, stack, variables, words, depth):
    if depth > 50:
        raise ValueError("recursão demais")
    for token in text.split():
        is_number, value = _number(token)
        if is_number:
            stack.append(value)
        elif token in BINARY:
            if len(stack) < 2:
                raise ValueError(f"pilha vazia em: {token}")
            b, a = stack.pop(), stack.pop()
            stack.append(BINARY[token](a, b))
        elif token in UNARY:
            if not stack:
                raise ValueError(f"pilha vazia em: {token}")
            stack.append(UNARY[token](stack.pop()))
        elif token in STACK_NEEDS:
            if len(stack) < STACK_NEEDS[token]:
                raise ValueError(f"pilha vazia em: {token}")
            if token == "dup":
                stack.append(stack[-1])
            elif token == "swap":
                stack[-2], stack[-1] = stack[-1], stack[-2]
            elif token == "drop":
                stack.pop()
            else:
                stack.append(stack[-2])
        elif token in words:
            _run(words[token], stack, variables, words, depth + 1)
        elif token in variables:
            stack.append(variables[token])
        else:
            raise ValueError(f"palavra desconhecida: {token}")


def rpn(text, variables=None, words=None):
    stack = []
    _run(text, stack, variables or {}, words or {}, 0)
    if len(stack) != 1:
        raise ValueError("expressão vazia" if not stack else "sobraram valores na pilha")
    return stack[0]


def rpn_trace(text, variables=None, words=None):
    stack, steps = [], []
    for token in text.split():
        _run(token, stack, variables or {}, words or {}, 0)
        steps.append(list(stack))
    return steps
