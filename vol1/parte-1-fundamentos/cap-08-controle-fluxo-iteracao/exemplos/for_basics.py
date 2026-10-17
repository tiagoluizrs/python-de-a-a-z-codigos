"""O que o for aceita: qualquer iteravel."""
import tempfile
from pathlib import Path

for letter in "abc":                       # str: um caractere por vez
    print(letter, end=" ")
print()

for point in (10, 20, 30):                 # tuple
    print(point, end=" ")
print()

prices = {"apple": 3.5, "pear": 4.0}
for key in prices:                         # dict: itera as CHAVES
    print(key, end=" ")
print()
for key, value in prices.items():          # pares (chave, valor)
    print(f"{key}={value}", end=" ")
print()

for number in {3}:                         # set (ordem nao garantida)
    print(number)

# arquivo: uma linha por vez, sem carregar o arquivo inteiro
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "names.txt"
    path.write_text("ana\nbia\ncaio\n", encoding="utf-8")
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            print(repr(line))

# o nome da variavel do for continua existindo depois do laco
for i in range(3):
    pass
print("depois do laco, i =", i)

# laco sobre iteravel vazio: o corpo nunca roda, i nao e criado
for j in []:
    pass
try:
    print(j)
except NameError as error:
    print("NameError:", error)
