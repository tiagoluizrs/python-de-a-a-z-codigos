"""O módulo operator: os operadores como funções."""
import functools
import operator

numbers = [3, 1, 4, 1, 5]
print(functools.reduce(operator.add, numbers),
      functools.reduce(operator.mul, numbers))
print(list(map(operator.neg, numbers)))
print(sorted(zip("abc", [3, 1, 2]), key=operator.itemgetter(1)))
print(operator.lt(1, 2), operator.contains([1, 2], 2), operator.index(5))

# Versões "in-place"
data = [1]
operator.iadd(data, [2])
print(data)
print(operator.iadd(5, 1))                      # em imutáveis, devolve novo

# Cada operador tem um nome em dunder e outro sem
print(operator.add is operator.__add__)
