"""Views são dinâmicas; alterar durante a iteração; ordem e igualdade."""
from collections import OrderedDict

stock = {"apple": 3, "pear": 5}
keys, values, items = stock.keys(), stock.values(), stock.items()
print(keys, values, items)
stock["kiwi"] = 7                       # as views enxergam a mudança
print(keys, list(values), len(items))

# Views de chaves e itens se comportam como conjuntos
print(keys & {"apple", "fig"}, sorted(keys - {"apple"}))
print(items & {("pear", 5)})
try:
    keys[0]
except TypeError as error:
    print("TypeError:", error)

# Alterar o tamanho durante a iteração
try:
    for key in stock:
        if stock[key] < 6:
            del stock[key]
except RuntimeError as error:
    print("RuntimeError:", error)
print(stock)
stock = {"apple": 3, "pear": 5, "kiwi": 7}
for key in list(stock):                 # snapshot das chaves
    if stock[key] < 6:
        del stock[key]
print(stock)
stock = {"apple": 3, "pear": 5, "kiwi": 7}
stock = {k: v for k, v in stock.items() if v >= 6}   # ou reconstruir
print(stock)
# Trocar o valor de chave existente durante o laço é permitido
for key in stock:
    stock[key] += 1
print(stock)

# Ordem de inserção: garantida, mas NÃO afeta a igualdade
x = {"a": 1, "b": 2}
y = {"b": 2, "a": 1}
print(x == y, list(x), list(y))
print(OrderedDict(x) == OrderedDict(y))
# Reatribuir uma chave existente não muda sua posição
x["a"] = 10
print(x)
# Remover e inserir de novo manda a chave para o fim
del x["a"]
x["a"] = 10
print(x)
