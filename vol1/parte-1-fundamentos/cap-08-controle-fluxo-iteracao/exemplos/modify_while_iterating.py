"""Alterar uma colecao enquanto ela e percorrida."""

# 1) lista: o laco usa um indice interno que continua subindo
numbers = [2, 4, 6, 8]
for number in numbers:
    print("visitando", number, "| lista agora:", numbers)
    numbers.remove(number)
print("resultado:", numbers)

# 2) acrescentar durante o laco: pode nunca terminar
items = [1]
for count, item in enumerate(items):
    if count == 5:
        break                  # sem este break seria infinito
    items.append(item + 1)
print(items)

# 3) dict: o Python detecta e levanta erro
stock = {"a": 0, "b": 5, "c": 0}
try:
    for key, qty in stock.items():
        if qty == 0:
            del stock[key]
except RuntimeError as error:
    print("RuntimeError:", error)
print("estado apos o erro:", stock)    # "a" ja tinha sido removido

# 3b) mudar so os VALORES e permitido (o tamanho nao muda)
for key in stock:
    stock[key] += 1
print(stock)

# 4) set tambem
letters = {"a", "b", "c"}
try:
    for letter in letters:
        letters.add(letter + "x")
except RuntimeError as error:
    print("RuntimeError:", error)

# solucoes
numbers = [2, 4, 6, 8, 3]
numbers[:] = [n for n in numbers if n % 2 != 0]   # mesma lista
print(numbers)

stock = {"a": 0, "b": 5, "c": 0}
for key in list(stock):                  # itera sobre uma COPIA
    if stock[key] == 0:
        del stock[key]
print(stock)

stock = {"a": 0, "b": 5, "c": 0}
stock = {k: v for k, v in stock.items() if v != 0}   # novo dict
print(stock)

# iterar de tras para frente tambem funciona em listas
numbers = [2, 4, 6, 8, 3]
for index in range(len(numbers) - 1, -1, -1):
    if numbers[index] % 2 == 0:
        del numbers[index]
print(numbers)
