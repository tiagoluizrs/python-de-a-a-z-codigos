"""Precedência, associatividade e ordem de avaliação."""
print(2 + 3 * 4 ** 2)        # 50
print(not 1 == 2)            # True: not vem DEPOIS de ==  -> not (1 == 2)
print(1 or 0 and 0)          # 1:    and vem antes de or    -> 1 or (0 and 0)
print(5 - 3 - 1, 2 ** 3 ** 2)  # 1 512 (esquerda->direita; ** da direita)

order = []
def trace(label, value):
    order.append(label)
    return value

trace("f", 1) + trace("g", 2) * trace("h", 3)
print(order)                 # ['f', 'g', 'h']: operandos SEMPRE da esquerda para a direita

# [*L for L in lists]  (3.15, PEP 798): desempacotar dentro de comprehension
lists = [[1, 2], [3], [4, 5]]
print([*items for items in lists])        # [1, 2, 3, 4, 5]
print({**d for d in [{"a": 1}, {"b": 2}]})  # {'a': 1, 'b': 2}
