"""A armadilha do late binding e suas três correções."""
from functools import partial

# O bug: todas as funções compartilham a MESMA célula de i
fns = []
for i in range(3):
    fns.append(lambda: i)
print([f() for f in fns], "i depois do laço:", i)

# Funções criadas no laço compartilham a variável
print(fns[0].__closure__ is None)   # i é global aqui, sem célula

# Dentro de uma função, o i vira variável livre (com célula)
def build():
    result = []
    for i in range(3):
        result.append(lambda: i)
    return result


built = build()
print([f() for f in built])
print(built[0].__closure__[0] is built[1].__closure__[0])

# Correção 1: argumento padrão (avaliado quando o lambda é criado)
fixed1 = [lambda i=i: i for i in range(3)]
print([f() for f in fixed1])


# Correção 2: functools.partial (congela o argumento)
def show(i):
    return i


fixed2 = [partial(show, i) for i in range(3)]
print([f() for f in fixed2])


# Correção 3: fábrica (cada chamada cria um escopo novo)
def make_show(i):
    return lambda: i


fixed3 = [make_show(i) for i in range(3)]
print([f() for f in fixed3])

# Efeito colateral do default: a função aceita um argumento extra
print(fixed1[0](99))

# A mesma armadilha em uma comprehension de lambdas
print([f() for f in [lambda: j for j in "abc"]])
