"""Counter e defaultdict: contar e agrupar."""
import timeit
from collections import Counter, defaultdict

c = Counter("abracadabra")
print(c.most_common(2), c["z"], c.total(), "z" in c)          # ausente: 0, e NÃO cria a chave
print(sorted(c.elements()))

# Aritmética de multiconjuntos: + e | somam/maximizam; - e & descartam não positivos
a, b = Counter(a=3, b=1), Counter(a=1, b=5)
print(a + b, a - b, a & b, a | b)

# subtract() mantém negativos; o operador unário + os remove
c2 = Counter(a=1)
c2.subtract(Counter(a=3))
print(c2, +c2)

# Contagem de palavras
text = "a b a c b a"
print(Counter(text.split()).most_common())

# defaultdict: valor inicial automático
groups = defaultdict(list)
for word in ["ana", "bia", "alan", "bruno", "carla"]:
    groups[word[0]].append(word)
print(dict(groups))

# A leitura de chave ausente CRIA a entrada
dd = defaultdict(int)
print(dd["x"], dict(dd), "y" in dd, dd.get("y"), "y" in dd)

# default_factory é chamada SEM argumentos (use lambda para valores específicos)
dd2 = defaultdict(lambda: "n/d")
print(dd2["k"])

# Dicionário de dicionários com contagem
nested = defaultdict(lambda: defaultdict(int))
nested["ana"]["a"] += 1
nested["ana"]["b"] += 2
print({k: dict(v) for k, v in nested.items()})

# Custos: contar 200 mil palavras
words = ["a", "b", "a", "c"] * 50_000


def manual(ws):
    d = {}
    for w in ws:
        d[w] = d.get(w, 0) + 1
    return d


def with_defaultdict(ws):
    d = defaultdict(int)
    for w in ws:
        d[w] += 1
    return d


for label, fn in [("Counter(words)", lambda: Counter(words)), ("dict.get manual", lambda: manual(words)),
                  ("defaultdict(int)", lambda: with_defaultdict(words))]:
    seconds = min(timeit.repeat(fn, number=5, repeat=3)) / 5
    print(f"  {label:<20}{seconds * 1e3:6.1f} ms")
