"""range nao cria lista: e uma formula (start, stop, step)."""
import sys
import timeit

small, huge = range(10), range(10**12)
print(sys.getsizeof(small), sys.getsizeof(huge))   # mesmo tamanho
print(len(huge), huge[-1], huge[5:8])

# in e feito por aritmetica, sem percorrer
print(999_999_999_999 in huge)
big = range(0, 10**12, 7)
print(7 * 123456 in big, 7 * 123456 + 1 in big)

# a lista equivalente seria gigantesca
print(sys.getsizeof(list(range(10**6))), "bytes para 1 milhao")

numbers = list(range(10**6))
rng = range(10**6)
print("in list:", round(timeit.timeit(
    lambda: 999_999 in numbers, number=20) / 20 * 1e3, 2), "ms")
print("in range:", round(timeit.timeit(
    lambda: 999_999 in rng, number=20) / 20 * 1e9), "ns")

# range e um iteravel REUTILIZAVEL (nao e iterador)
r = range(3)
print(list(r), list(r))
print(iter(r) is iter(r))
print(type(iter(r)).__name__)

# atributos
print(r.start, r.stop, r.step, range(10, 0, -2).step)
print(range(0, 5) == range(0, 5, 1), range(0) == range(5, 5))

# Por dentro do for sobre lista: um indice interno
numbers = [1, 2, 3, 4]
iterator = iter(numbers)
print(iterator.__reduce__())       # (iter, (lista,), indice_atual)
next(iterator)
print(iterator.__reduce__())
numbers.pop()                      # alteracao visivel ao iterador
print(list(iterator))
