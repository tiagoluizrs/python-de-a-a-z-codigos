"""Expressoes geradoras: avaliacao preguicosa e parenteses opcionais."""
import dis

calls = []


def noisy(x):
    calls.append(x)
    return x * x


gen = (noisy(x) for x in range(5))
print("criou, chamadas:", calls)
print(next(gen), next(gen), "chamadas:", calls)

# o iteravel mais externo e avaliado ja na criacao; o resto, nao
def source():
    print("  source() avaliada")
    return [1, 2, 3]


g = (x for x in source())
print("depois de criar g")
list(g)

try:
    bad = (x for x in 5)
except TypeError as exc:
    print("na criacao:", exc)

lazy = (1 / x for x in [1, 0])
print("criado sem erro")
try:
    list(lazy)
except ZeroDivisionError as exc:
    print("so ao consumir:", exc)

# parenteses opcionais apenas se for o unico argumento
print(sum(x for x in range(4)))
try:
    compile("sum(x for x in range(4), 10)", "<s>", "eval")
except SyntaxError as exc:
    print("SyntaxError:", exc.msg)
print(sum((x for x in range(4)), 10))
print(sorted((x for x in "cab"), reverse=True))

# a variavel do laco nao vaza
[i for i in range(3)]
try:
    print(i)
except NameError as exc:
    print(exc)

dis.dis((x for x in range(3)))
