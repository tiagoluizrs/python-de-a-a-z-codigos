"""Indexação e fatiamento: sequence[start:stop:step]."""
numbers = list(range(10))

print(numbers[2:5])        # [2, 3, 4]   (stop é exclusivo)
print(numbers[-3:])        # [7, 8, 9]
print(numbers[::3])        # [0, 3, 6, 9]
print(numbers[::-1])       # [9, 8, ..., 0]: cópia invertida
print(numbers[100:])       # []          (fatiar fora do limite NÃO levanta erro)
print(numbers[-100:2])     # [0, 1]

# Fatias são objetos
every_other = slice(1, 8, 2)
print(numbers[every_other], every_other.indices(10))

# Em listas, fatias aceitam atribuição e remoção
numbers[2:5] = ["a"]       # substitui 3 itens por 1: a lista ENCOLHE
print(numbers)             # [0, 1, 'a', 5, 6, 7, 8, 9]
numbers[::2] = [0] * len(numbers[::2])   # fatia com passo exige o mesmo tamanho
print(numbers)             # [0, 1, 0, 5, 0, 7, 0, 9]
try:
    numbers[::2] = [1]
except ValueError as error:
    print(error)           # attempt to assign sequence of size 1 to extended slice of size 4
del numbers[::2]
print(numbers)             # [1, 5, 7, 9]

# Índice simples fora do limite LEVANTA erro; fatia não
try:
    numbers[10]
except IndexError as error:
    print(error)           # list index out of range
