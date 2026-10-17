"""Armadilhas clássicas com listas."""
import copy

# 1) [[0] * 2] * 2 repete a MESMA linha
grid = [[0] * 2] * 2
grid[0][0] = 1
print(grid)                       # [[1, 0], [1, 0]]
grid = [[0] * 2 for _ in range(2)]
grid[0][0] = 1
print(grid)                       # [[1, 0], [0, 0]]

# 2) Remover itens enquanto itera pula elementos
numbers = [2, 4, 6, 8]
for number in numbers:
    if number % 2 == 0:
        numbers.remove(number)
print(numbers)                    # [4, 8]  <- esperado: []

numbers = [2, 4, 6, 8]
numbers[:] = [n for n in numbers if n % 2 != 0]   # filtra "no lugar"
print(numbers)                    # []

# 3) sort() devolve None
values = [3, 1, 2]
print(values.sort(), values)      # None [1, 2, 3]
print(sorted([3, 1, 2]))          # sorted() devolve uma lista nova

# 4) Cópia rasa × cópia profunda
original = [[1], [2]]
shallow = original.copy()
deep = copy.deepcopy(original)
original[0].append(9)
print(shallow, deep)              # [[1, 9], [2]] [[1], [2]]

# 5) Tipos misturados não ordenam
try:
    sorted([1, "a"])
except TypeError as error:
    print(error)                  # '<' not supported between instances of 'str' and 'int'
