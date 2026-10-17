"""Variáveis são nomes (etiquetas) presos a objetos."""
import sys

x = 42
print(f"id={id(x)}  type={type(x).__name__}  value={x}")

# Dois nomes, um objeto
a = [1, 2, 3]
b = a
print(a is b)          # True: mesma identidade
b.append(4)
print(a)               # [1, 2, 3, 4]: o objeto mudou, os dois nomes veem

# Contagem de referências (no 3.14+, getrefcount(a) já começa em 2)
print(sys.getrefcount(a))   # 3: a, b e o argumento da chamada
del b                       # remove o nome, não o objeto
print(sys.getrefcount(a))   # 2

# Reatribuir um nome não altera o objeto antigo
text = "python"
before = id(text)
text = text + "-book"
print(before == id(text))   # False: nasceu um novo objeto str
