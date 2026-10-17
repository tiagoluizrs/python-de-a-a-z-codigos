"""Padroes classicos de laco."""
from collections import Counter

scores = [72, 85, 90, 64, 85, 100]

# acumulador
total = 0
for score in scores:
    total += score
print("total:", total, "media:", round(total / len(scores), 1))

# maximo manual (e por que o valor inicial importa)
best = scores[0]
for score in scores[1:]:
    if score > best:
        best = score
print("maximo:", best, "== max():", max(scores))

# contador
word_count = {}
for word in "to be or not to be".split():
    word_count[word] = word_count.get(word, 0) + 1
print(word_count)
print(Counter("to be or not to be".split()).most_common(2))

# agrupamento
by_size = {}
for word in ["a", "bb", "cc", "d", "eee"]:
    by_size.setdefault(len(word), []).append(word)
print(by_size)

# flag (estado entre voltas)
seen_error = False
for line in ["ok", "ok", "ERROR disk", "ok"]:
    if line.startswith("ERROR"):
        seen_error = True
print("houve erro:", seen_error)

# dois ponteiros: palindromo sem criar copia invertida
def is_palindrome(text):
    left, right = 0, len(text) - 1
    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1
    return True


print(is_palindrome("arara"), is_palindrome("python"))

# dois ponteiros em lista ordenada: par com soma alvo
def pair_with_sum(sorted_values, target):
    left, right = 0, len(sorted_values) - 1
    while left < right:
        current = sorted_values[left] + sorted_values[right]
        if current == target:
            return sorted_values[left], sorted_values[right]
        if current < target:
            left += 1
        else:
            right -= 1
    return None


print(pair_with_sum([1, 3, 4, 6, 9, 11], 10))

# janela deslizante: maior soma de k elementos consecutivos, O(n)
def best_window_sum(values, k):
    window = sum(values[:k])
    best = window
    for i in range(k, len(values)):
        window += values[i] - values[i - k]   # entra um, sai outro
        best = max(best, window)
    return best


print(best_window_sum([2, 1, 5, 1, 3, 2], 3))

# aninhados: pares distintos de uma lista (i < j)
names = ["ana", "bia", "caio"]
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        print(names[i], names[j])

# sair de dois niveis: funcao + return
def find_cell(grid, wanted):
    for row_index, row in enumerate(grid):
        for col_index, cell in enumerate(row):
            if cell == wanted:
                return row_index, col_index
    return None


print(find_cell([[1, 2], [3, 4]], 4))
