"""O que é falso em Python: os valores 'vazios' ou 'zero'."""
values = [None, False, 0, 0.0, 0j, "", b"", [], (), {}, set(), range(0)]
for value in values:
    print(f"{value!r:>12} -> {bool(value)}")

print("---- verdadeiros ----")
for value in [-1, 0.1, " ", "0", "False", [0], [[]], (None,)]:
    print(f"{value!r:>12} -> {bool(value)}")
