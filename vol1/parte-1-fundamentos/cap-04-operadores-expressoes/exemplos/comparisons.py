"""Comparações: encadeamento, tipos diferentes e igualdade numérica."""
x = 5
print(1 < x < 10)            # True: equivale a (1 < x) and (x < 10), com x avaliado UMA vez
print(1 < x > 3 < 10)        # True: encadeamentos podem misturar operadores
print(1 == 1.0 == True)      # True: int, float e bool comparam por valor numérico
print((1, 2, 3) < (1, 2, 4), "abc" < "abd", "Z" < "a")   # True True True (por ponto de código)
print([1, 2] == [1, 2], [1, 2] is [1, 2])                # True False

nan = float("nan")
print(nan == nan, nan != nan, nan < 1, nan > 1)          # False True False False

try:
    1 < "2"
except TypeError as error:
    print(error)             # '<' not supported between instances of 'int' and 'str'

calls = []
def f(label, value):
    calls.append(label)
    return value
f("a", 5) < f("b", 3) < f("c", 9)   # para no segundo (curto-circuito)
print(calls)                 # ['a', 'b']: "c" nem foi avaliado
