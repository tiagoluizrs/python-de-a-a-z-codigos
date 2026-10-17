"""range, enumerate, zip, reversed, sorted e desempacotamento."""

print(list(range(0, 10, 3)))        # passo positivo
print(list(range(10, 0, -3)))       # passo negativo: stop exclusivo
print(list(range(5, 5)), list(range(5, 0)))   # vazios
try:
    range(0, 10, 0)
except ValueError as error:
    print("ValueError:", error)
try:
    range(0, 1.5)
except TypeError as error:
    print("TypeError:", error)

fruits = ["apple", "banana", "cherry"]
for position, fruit in enumerate(fruits, start=1):
    print(position, fruit)

names = ["Ana", "Bia", "Caio"]
ages = [30, 25]
print(list(zip(names, ages)))       # para no mais curto, em silencio
try:
    list(zip(names, ages, strict=True))
except ValueError as error:
    print("ValueError:", error)

# zip em dois sentidos: "transpor" e reconstruir
pairs = [("a", 1), ("b", 2), ("c", 3)]
letters, numbers = zip(*pairs)
print(letters, numbers)

# reversed: sem copiar; sorted: copia e ordena
for item in reversed(fruits):
    print(item, end=" ")
print()
for item in sorted(fruits, key=len, reverse=True):
    print(item, end=" ")
print()
print(fruits)                        # a original nao mudou

# desempacotamento no cabecalho
rows = [("Ana", (30, "SP")), ("Bia", (25, "RJ"))]
for name, (age, state) in rows:
    print(name, age, state)

first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)
for head, *tail in [(1, 2, 3), (4, 5)]:
    print(head, tail)

# enumerate sobre dict.items(): parenteses obrigatorios
for index, (key, value) in enumerate({"x": 1, "y": 2}.items()):
    print(index, key, value)

# ordem de insercao do dict e preservada (desde o 3.7)
config = {"b": 2, "a": 1}
for key in sorted(config):
    print(key, config[key])
