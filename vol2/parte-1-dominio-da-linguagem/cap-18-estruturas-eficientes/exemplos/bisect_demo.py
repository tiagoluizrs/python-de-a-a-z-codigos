"""bisect: busca binária e listas sempre ordenadas."""
import bisect
import timeit

data = [1, 2, 2, 2, 3]
print(bisect.bisect_left(data, 2), bisect.bisect_right(data, 2), bisect.bisect(data, 2))

# Inserir mantendo a ordem
scores = [10, 30, 50]
bisect.insort(scores, 40)
print(scores)


# Faixas: nota -> conceito
def grade(score, breakpoints=(60, 70, 80, 90), letters="FDCBA"):
    return letters[bisect.bisect(breakpoints, score)]


print([grade(s) for s in (33, 60, 75, 89, 90, 100)])

# key= (3.10+): buscar em lista de registros
records = [("ana", 20), ("bia", 25), ("caio", 31)]
print(bisect.bisect_left(records, 25, key=lambda r: r[1]))

# Contar quantos itens estão em um intervalo [lo, hi]
ordered = [1, 3, 3, 5, 8, 13, 21]
lo, hi = 3, 13
print(bisect.bisect_right(ordered, hi) - bisect.bisect_left(ordered, lo))

# Custos (100 mil itens ordenados)
big = list(range(100_000))
ns = dict(big=big, bisect=bisect)
for label, statement in [("bisect_left", "bisect.bisect_left(big, 77777)"), ("x in lista", "77777 in big")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=2000, repeat=3)) / 2000
    print(f"  {label:<14}{seconds * 1e6:9.2f} us")

# insort é O(n) por causa do deslocamento (a busca é O(log n), a inserção não)
ns2 = dict(big=list(range(100_000)), bisect=bisect)
seconds = min(timeit.repeat("bisect.insort(big, 50000)", globals=ns2, number=2000, repeat=3)) / 2000
print(f"  insort no meio  {seconds * 1e6:9.2f} us")
