"""O operador morsa (:=) atribui DENTRO de uma expressão (Python 3.8+)."""
import io
import re

stream = io.BytesIO(b"abcdefghij")
while chunk := stream.read(4):          # lê, atribui e testa em uma linha
    print(chunk)

data = [1, 5, 12, 20, 7]
big_squares = [square for n in data if (square := n * n) > 100]
print(big_squares)                       # [144, 400]

if match := re.search(r"(\d+)-(\d+)", "tel 555-1234"):
    print(match.group(1), match.group(2))

# Cuidado: use parênteses fora de instruções simples
print(total := 10 + 5)                   # 15 (e 'total' passa a existir)
