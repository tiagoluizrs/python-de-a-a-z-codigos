"""cmp_to_key, total_ordering e a estabilidade da ordenação."""
from functools import cmp_to_key, total_ordering

# cmp_to_key: adaptar uma função de comparação (estilo antigo) para key=
def by_length_then_alpha(a, b):
    if len(a) != len(b):
        return len(a) - len(b)
    return (a > b) - (a < b)


words = ["pera", "uva", "maçã", "kiwi", "figo", "abacate"]
print(sorted(words, key=cmp_to_key(by_length_then_alpha)))
print(sorted(words, key=lambda w: (len(w), w)))                 # o equivalente com tupla (preferível)

# Quando a tupla não serve: ordem "estranha" entre pares (maior número concatenado)
def concat_cmp(a, b):
    return -1 if a + b > b + a else (1 if a + b < b + a else 0)


nums = ["9", "34", "3", "30", "5"]
print("".join(sorted(nums, key=cmp_to_key(concat_cmp))))

# Estabilidade: itens iguais mantêm a ordem original
rows = [("ana", 2), ("bia", 1), ("caio", 2), ("dani", 1)]
print(sorted(rows, key=lambda r: r[1]))

# total_ordering e custo (resumo do Capítulo 10)
@total_ordering
class Version:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return self.n == other.n

    def __lt__(self, other):
        return self.n < other.n


print(Version(1) <= Version(2), Version(3) > Version(2), Version(1) >= Version(1))
