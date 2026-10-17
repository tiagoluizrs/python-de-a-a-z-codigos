"""Limite alto de recursão: em Python puro não usa a pilha C (3.12+)."""
import sys


def down(n):
    return 0 if n == 0 else 1 + down(n - 1)


def tail(n, acc=0):
    # recursão "de cauda": o Python NÃO a otimiza
    return acc if n == 0 else tail(n - 1, acc + 1)


sys.setrecursionlimit(1_000_000)
print(down(500_000))
print(tail(500_000))
try:
    sys.setrecursionlimit(10_000)
    tail(50_000)
except RecursionError as exc:
    print("RecursionError:", exc)
