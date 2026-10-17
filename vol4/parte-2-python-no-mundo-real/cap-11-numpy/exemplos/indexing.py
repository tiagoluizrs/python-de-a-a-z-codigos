"""Indexação: fatias (view), máscaras e índices por lista (cópia), e as armadilhas."""
import numpy as np

a = np.arange(20).reshape(4, 5)
print("a =\n", a)

# 1. índice básico e fatias: sempre VIEW
print("\na[1, 2]      =", a[1, 2], "| a[1][2] =", a[1][2], "(funciona, mas cria um array intermediário)")
print("a[:, 0]      =", a[:, 0], "(primeira coluna)")
print("a[::2, 1::2] =", a[::2, 1::2].tolist(), "(linhas alternadas, colunas ímpares)")
print("a[-1]        =", a[-1], "| a[..., -1] =", a[..., -1], "(Ellipsis: 'todos os eixos que faltam')")
print("a[:, None, 0].shape =", a[:, None, 0].shape, "(None cria um eixo novo de tamanho 1)")

# 2. máscara booleana: seleciona e devolve CÓPIA
mask = a % 3 == 0
print("\nmáscara (a % 3 == 0):\n", mask.astype(int))
print("a[mask]  =", a[mask], "| é cópia?", not np.shares_memory(a, a[mask]))
a2 = a.copy()
a2[a2 > 15] = -1                                  # atribuição por máscara escreve NO ORIGINAL
print("a2[a2 > 15] = -1 ->", a2[3].tolist())

# 3. E / OU / NÃO: operadores bit a bit com parênteses, nunca and/or/not
x = np.array([1, 5, 10, 15])
print("\n(x > 2) & (x < 12) =", (x > 2) & (x < 12), "| ~(x > 5) =", ~(x > 5))
try:
    x > 2 and x < 12
except ValueError as error:
    print("x > 2 and x < 12  -> ValueError:", str(error)[:50])
print("sem parênteses, x > 2 & x < 12 vira x > (2 & x) < 12:", end=" ")
try:
    print(x > 2 & x < 12)
except ValueError as error:
    print("ValueError (cadeia de comparação ambígua)")
print("any / all:", (x > 12).any(), (x > 0).all(), "| contagem:", (x > 4).sum(), "| posições:", np.flatnonzero(x > 4))

# 4. índices por lista ("fancy"): CÓPIA, e podem repetir e reordenar
rows = np.array([3, 0, 0])
print("\na[[3, 0, 0]] =", a[rows].tolist(), "| é cópia?", not np.shares_memory(a, a[rows]))
print("a[[0, 1], [2, 3]] (pares) =", a[[0, 1], [2, 3]], "| bloco a[np.ix_([0,1],[2,3])] =", a[np.ix_([0, 1], [2, 3])].tolist())

# 5. argmax/argsort/where devolvem POSIÇÕES; take_along_axis aplica
scores = np.array([[0.1, 0.7, 0.2], [0.8, 0.1, 0.1], [0.3, 0.3, 0.4]])
best = scores.argmax(axis=1)
print("\nargmax por linha:", best, "| valor do melhor:", np.take_along_axis(scores, best[:, None], axis=1).ravel())
print("np.where(cond) devolve índices:", np.where(scores > 0.5), "| (cond, a, b) escolhe valores")

# 6. atribuição por fatia e por índice
b = np.zeros(6, dtype=int)
b[1:4] = 7
b[[0, 5]] = [1, 2]
b[b == 0] = -9
print("\natribuição:", b)

# 7. a armadilha da view: modificar a fatia modifica o original (e funções também)
data = np.arange(10)
head = data[:3]
head *= 100
print("\ndata após head *= 100 :", data, "(head é view)")
safe = data[:3].copy()
safe += 1
print("com .copy() o original fica:", data[:3])


def normalize_in_place(v):
    v -= v.mean()                                # muda o array de quem chamou!


arr = np.array([1.0, 2.0, 3.0])
normalize_in_place(arr)
print("função que usa -= no argumento mudou o chamador:", arr)

# 8. np.take e put: alternativas com nomes que documentam a intenção
print("\nnp.take(a, [0, 2], axis=1) =", np.take(a, [0, 2], axis=1).tolist())

# 9. ordenação e busca
v = np.array([30, 10, 20, 10, 40])
print("\nsort:", np.sort(v), "| argsort:", np.argsort(v, kind="stable"), "| unique:", np.unique(v),
      "| unique counts:", np.unique(v, return_counts=True)[1])
sorted_v = np.sort(v)
print("searchsorted (bisect vetorizado):", np.searchsorted(sorted_v, [5, 20, 25, 50]))
print("isin:", np.isin(v, [10, 40]), "| top-2 sem ordenar tudo (argpartition):", np.sort(v[np.argpartition(v, -2)[-2:]]))
