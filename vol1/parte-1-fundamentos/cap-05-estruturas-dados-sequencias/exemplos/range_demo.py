"""range: uma sequência 'virtual' que calcula os valores sob demanda."""
import sys

r = range(0, 10**18, 7)
print(len(r))                       # 142857142857142858
print(7 * 10**15 in r, 10**17 in r)   # True False: teste de pertinência em O(1), por aritmética
print(r[5], r[-1])                  # indexação direta
print(sys.getsizeof(range(10)), sys.getsizeof(range(10**18)))   # 48 48

print(list(range(10, 0, -3)))       # [10, 7, 4, 1]
print(range(10)[2:8:2], range(10)[::-1])   # fatiar um range devolve outro range
print(range(0, 10, 3) == range(0, 12, 3))  # True: mesmos elementos
