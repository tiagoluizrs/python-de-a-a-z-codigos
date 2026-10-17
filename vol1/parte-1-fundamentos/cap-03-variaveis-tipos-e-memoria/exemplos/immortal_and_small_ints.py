"""Objetos imortais e o cache de inteiros pequenos (detalhes do CPython)."""
import sys

IMMORTAL_THRESHOLD = 2**30  # contagens enormes indicam objeto imortal

for obj in (None, True, 5, int("1000")):
    print(f"{obj!r:>6} refcount={sys.getrefcount(obj)}")

# Descobrindo o intervalo do cache nesta versão (int(str(n)) evita a
# otimização do compilador, que reaproveita constantes iguais)
cached = [n for n in range(-300, 20_000)
          if sys.getrefcount(int(str(n))) > IMMORTAL_THRESHOLD]
print(f"Cached small ints: {min(cached)}..{max(cached)}")

a = int("100000")
b = int("100000")
print(a == b, a is b)   # True False: iguais em valor, objetos distintos
