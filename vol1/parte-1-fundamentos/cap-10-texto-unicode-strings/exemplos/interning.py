"""Interning de strings: identificadores sim, texto arbitrário não."""
import sys
import timeit

a = "hello_world"
b = "hello" + "_world"                  # dobrado pelo compilador
c = "".join(["hello", "_world"])        # montado em tempo de execução
print(a is b, a is c, a == c, a is sys.intern(c))

x = "hello world"                       # tem espaço: não é identificador
y = "hello world"
print(x is y)                           # mesma constante no mesmo módulo

# chaves de dicionário vindas de fora (ex.: lidas de arquivo)
words = [("w" + str(i % 100)) for i in range(100_000)]
words2 = [sys.intern(w) for w in words]
print(len({id(w) for w in words}), len({id(w) for w in words2}))

lookup = {w: i for i, w in enumerate(set(words2))}
probe_a = "w" + "42"
probe_b = sys.intern(probe_a)
n = 2_000_000
t_a = timeit.timeit(lambda: lookup[probe_a], number=n)
t_b = timeit.timeit(lambda: lookup[probe_b], number=n)
print(f"lookup normal   {t_a / n * 1e9:6.1f} ns")
print(f"lookup interned {t_b / n * 1e9:6.1f} ns")
