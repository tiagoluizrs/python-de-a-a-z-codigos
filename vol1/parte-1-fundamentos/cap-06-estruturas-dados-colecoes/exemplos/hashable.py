"""Chaves precisam ser hasheáveis; igualdade e hash andam juntos."""
good = {1: "int", "a": "str", (1, 2): "tuple", frozenset({1}): "fs"}
print(good)
for bad in ([1], {1}, {"a": 1}):
    try:
        {bad: 1}
    except TypeError as error:
        print("TypeError:", error)
try:
    {(1, [2]): 1}
except TypeError as error:
    print("TypeError:", error)

# 1, 1.0 e True são iguais e têm o mesmo hash: viram UMA chave
mixed = {1: "int", 1.0: "float", True: "bool"}
print(mixed, hash(1) == hash(1.0) == hash(True))
# NaN: nunca é igual a si mesmo, mas a identidade basta para achá-lo
nan = float("nan")
box = {nan: 1}
print(box[nan], box.get(float("nan")))
print(hash(42), hash("abc") != hash("abd"))
