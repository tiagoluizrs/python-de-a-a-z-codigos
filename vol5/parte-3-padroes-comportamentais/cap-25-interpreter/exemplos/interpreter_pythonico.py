"""Interpreter em Python: reaproveitar a gramática do Python (ast), compilar para closures e interpretadores de tabela, sem classes por regra."""
import ast
import operator
import time


# --- 1. antes de escrever uma linguagem: os dados já têm formato pronto ---
print("literal_eval:", ast.literal_eval("{'a': [1, 2.5, None], 'ok': True}"), "| config, JSON-like e literais: seguro, sem escrever interpretador")
try:
    ast.literal_eval("__import__('os').getcwd()")
except ValueError as error:
    print("  literal_eval recusa código:", type(error).__name__)

# --- 2. o perigo: o eval executa QUALQUER coisa ---
print("\neval do texto do usuário:", eval("__import__('math').sqrt(16)"), "(um import e uma chamada arbitrária; troque o sqrt por algo destrutivo e o texto de um formulário apaga o seu disco)")
print("eval com __builtins__ vazio ainda é furado:", eval("().__class__.__name__", {"__builtins__": {}}), "(o acesso a atributos continua; é por esse caminho que a 'caixa de areia' do eval é quebrada)")


# --- 3. reaproveitar a GRAMÁTICA do Python: o analisador já existe ---
CMP = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}


def walk(node, ctx):
    """Percorre a árvore do Python permitindo SÓ um subconjunto (lista branca): o resto é recusado."""
    match node:
        case ast.Constant(value) if value is None or isinstance(value, (bool, int, float, str)):
            return value
        case ast.Name(id=name):
            if name not in ctx:
                raise KeyError(f"variável indefinida: {name}")
            return ctx[name]
        case ast.BoolOp(ast.And(), values):
            result = True
            for value in values:
                result = walk(value, ctx)
                if not result:
                    return result                          # curto-circuito, como no Python
            return result
        case ast.BoolOp(ast.Or(), values):
            result = False
            for value in values:
                result = walk(value, ctx)
                if result:
                    return result
            return result
        case ast.UnaryOp(ast.Not(), operand):
            return not walk(operand, ctx)
        case ast.Compare(left, ops, comparators):
            current = walk(left, ctx)
            for op, right_node in zip(ops, comparators):   # a cadeia 18 <= age < 65
                right = walk(right_node, ctx)
                if not CMP[type(op)](current, right):
                    return False
                current = right
            return True
        case ast.Tuple(elts) | ast.List(elts):
            return tuple(walk(e, ctx) for e in elts)
        case _:
            raise ValueError(f"expressão não permitida: {type(node).__name__}")


def safe_eval(text, ctx):
    return walk(ast.parse(text, mode="eval").body, ctx)


RULE = "age >= 18 and (country in ('BR', 'PT') or vip) and not banned"
CTX = {"age": 20, "country": "PT", "vip": False, "banned": False}
print("\nsafe_eval (a sintaxe é a do Python; nenhum analisador escrito):", safe_eval(RULE, CTX), "|", safe_eval("18 <= age < 65", CTX), "(cadeia de comparações de graça)")
for attack in ("__import__('os').getcwd()", "().__class__", "[x for x in range(9)]", "lambda: 1", "age.real"):
    try:
        safe_eval(attack, CTX)
    except ValueError as error:
        print(f"  {attack:28} -> {error}")


# --- 4. compilar para closures: a árvore é percorrida UMA vez, na criação ---
def to_closure(node):
    match node:
        case ast.Constant(value):
            return lambda ctx: value
        case ast.Name(id=name):
            return lambda ctx: ctx[name]
        case ast.BoolOp(ast.And(), values):
            fns = [to_closure(v) for v in values]

            def and_(ctx):
                result = True
                for fn in fns:
                    result = fn(ctx)
                    if not result:
                        return result
                return result

            return and_
        case ast.BoolOp(ast.Or(), values):
            fns = [to_closure(v) for v in values]

            def or_(ctx):
                result = False
                for fn in fns:
                    result = fn(ctx)
                    if result:
                        return result
                return result

            return or_
        case ast.UnaryOp(ast.Not(), operand):
            fn = to_closure(operand)
            return lambda ctx: not fn(ctx)
        case ast.Compare(left, [op], [right]) if type(op) in CMP:
            fl, fr, compare = to_closure(left), to_closure(right), CMP[type(op)]
            return lambda ctx: compare(fl(ctx), fr(ctx))
        case ast.Tuple(elts):
            fns = [to_closure(e) for e in elts]
            return lambda ctx: tuple(fn(ctx) for fn in fns)
        case _:
            raise ValueError(f"expressão não permitida: {type(node).__name__}")        # recusada na CRIAÇÃO, não na centésima chamada


def compile_rule(text):
    return to_closure(ast.parse(text, mode="eval").body)


rule = compile_rule(RULE)
print("\nclosure compilada:", rule(CTX), rule({**CTX, "banned": True}), "| regra inválida é recusada ao compilar:", end=" ")
try:
    compile_rule("age >= 18 and open('/etc/passwd')")
except ValueError as error:
    print(error)


# --- 5. a tabela de despacho: um interpretador SEM classes (a calculadora de pilha) ---
BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "//": operator.floordiv, "%": operator.mod, "**": operator.pow, "max": max, "min": min}
UNARY = {"neg": operator.neg, "abs": abs}


def number(token):
    for kind in (int, float):
        try:
            return True, kind(token)
        except ValueError:
            pass
    return False, None


def run(text, stack, variables, words, depth):
    if depth > 50:
        raise ValueError("recursão demais")
    for token in text.split():
        is_number, value = number(token)
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
        elif token == "dup":
            stack.append(stack[-1])
        elif token in words:                               # uma palavra definida pelo usuário: um MACRO que roda na mesma pilha
            run(words[token], stack, variables, words, depth + 1)
        elif token in variables:
            stack.append(variables[token])
        else:
            raise ValueError(f"palavra desconhecida: {token}")


def rpn(text, variables=None, words=None):
    stack = []
    run(text, stack, variables or {}, words or {}, 0)
    if len(stack) != 1:
        raise ValueError("expressão vazia" if not stack else "sobraram valores na pilha")
    return stack[0]


print("\npilha:", rpn("3 4 + 2 *"), "| com variável:", rpn("x 2 ** y +", {"x": 3, "y": 1}), "| palavra do usuário (sq = dup *):", rpn("5 sq 1 +", words={"sq": "dup *"}))
try:
    rpn("1 loop", words={"loop": "loop"})
except ValueError as error:
    print("palavra que chama a si mesma:", error)


# --- 6. o custo ---
def best(fn, n=50_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


code = compile(ast.parse(RULE, mode="eval"), "<rule>", "eval")
tree = ast.parse(RULE, mode="eval").body
by_hand = lambda c: c["age"] >= 18 and (c["country"] in ("BR", "PT") or c["vip"]) and not c["banned"]

print(
    f"\npor avaliação | à mão {best(lambda: by_hand(CTX)):5.2f} µs | compile()+eval (INSEGURO) {best(lambda: eval(code, {'__builtins__': {}}, CTX)):5.2f} µs | closure compilada {best(lambda: rule(CTX)):5.2f} µs | percorrer a árvore do ast {best(lambda: walk(tree, CTX)):5.2f} µs"
)
print(f"analisar o texto a cada avaliação (safe_eval): {best(lambda: safe_eval(RULE, CTX), 5_000):6.2f} µs | compilar a closure uma vez: {best(lambda: compile_rule(RULE), 5_000):6.2f} µs")
