"""Passagem de parâmetros: o objeto é compartilhado, o nome é local."""


def append_item(items: list, value) -> None:
    items.append(value)          # muta o objeto do chamador


def rebind(items: list) -> None:
    items = [99]                 # só move a etiqueta LOCAL
    print("dentro:", items)


def increment(n: int) -> int:
    n += 1                       # int é imutável: cria outro objeto
    return n


data = [1, 2]
append_item(data, 3)
print("depois de append_item:", data)
rebind(data)
print("depois de rebind:", data)

count = 10
increment(count)
print("count continua:", count)

# O parâmetro e o argumento são o MESMO objeto (a mesma identidade)
def show_id(param):
    return id(param)

print("mesmo id:", show_id(data) == id(data))

# Aliasing escondido em estruturas aninhadas
grid = [[0] * 2] * 2             # duas referências à MESMA linha
grid[0][0] = 7
print("grid ruim:", grid)
grid = [[0] * 2 for _ in range(2)]
grid[0][0] = 7
print("grid bom: ", grid)

# Imutável com conteúdo mutável
row = ([1], "x")
row[0].append(2)
print("tupla 'imutável' mudou:", row)
