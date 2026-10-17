"""Contagem e agrupamento manuais com dict."""
text = "the quick brown fox jumps over the lazy dog the end"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)
print(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3])

words = ["apple", "avocado", "banana", "blueberry", "cherry"]
by_letter = {}
for word in words:
    by_letter.setdefault(word[0], []).append(word)
print(by_letter)

# Mesmo resultado, com a forma "pedir perdão" (EAFP)
by_len = {}
for word in words:
    try:
        by_len[len(word)].append(word)
    except KeyError:
        by_len[len(word)] = [word]
print(by_len)
