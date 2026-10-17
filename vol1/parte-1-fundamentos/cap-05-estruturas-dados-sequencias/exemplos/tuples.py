"""Tuplas: registros imutáveis, empacotamento e desempacotamento."""
point = (3, 4)
single = (1,)                  # a vírgula faz a tupla, não os parênteses
empty = ()
print(type((1)), type(single), type(empty))

# Empacotar e desempacotar
x, y = point
first, *middle, last = range(6)
print(x, y, first, middle, last)    # 3 4 0 [1, 2, 3, 4] 5
(a, b), c = (1, 2), 3
a, b = b, a                         # troca sem variável temporária

# Hasheável: serve de chave de dicionário (desde que o conteúdo também seja)
distances = {(0, 0): 0, (1, 0): 1}
print(distances[(1, 0)])
try:
    hash((1, 2, [3]))
except TypeError as error:
    print(error)                    # unhashable type: 'list'

# Ordenação lexicográfica: útil para ordenar por vários critérios
people = [("Ana", 30), ("Bia", 25), ("Caio", 30), ("Dan", 25)]
print(sorted(people, key=lambda p: (-p[1], p[0])))   # idade desc, nome asc
print(sorted(people, key=lambda p: p[1]))            # estável: Bia antes de Dan
