"""Funções puras x efeitos colaterais."""


def sorted_copy(values):          # pura: não toca no argumento
    return sorted(values)


def sort_in_place(values):        # efeito colateral: altera o argumento
    values.sort()


data = [3, 1, 2]
print(sorted_copy(data), data)
print(sort_in_place(data), data)

# a mesma entrada, resultados diferentes: impura (depende de estado)
rate = 0.1


def price_with_tax(price):
    return price * (1 + rate)


print(price_with_tax(100))
rate = 0.2
print(price_with_tax(100))

# retornar tipos diferentes conforme o caso
def find_bad(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return False        # False == 0 !


print(find_bad(["a", "b"], "a") == find_bad(["a", "b"], "z"))
