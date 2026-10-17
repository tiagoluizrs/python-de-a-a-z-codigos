"""Exercício 5: otimize pelo ALGORITMO (os testes medem o ganho)."""
from collections import Counter  # noqa: F401  (pode ser útil)


def unique_naive(items):
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def unique_fast(items):
    """Mesmo resultado de ``unique_naive`` (ordem da primeira aparição), em
    tempo linear. Itens hasheáveis."""
    raise NotImplementedError


def common_naive(a, b):
    return [x for x in a if x in b]


def common_fast(a, b):
    """Mesmo resultado de ``common_naive`` (itens de ``a`` que estão em ``b``,
    na ordem e com as repetições de ``a``), sem busca linear em ``b``."""
    raise NotImplementedError


def pair_count_naive(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def pair_count_fast(nums, target):
    """Mesmo resultado de ``pair_count_naive`` (pares ``i < j`` com soma
    ``target``), em tempo linear."""
    raise NotImplementedError


def frequencies_naive(words):
    return {w: words.count(w) for w in words}


def frequencies_fast(words):
    """Mesmo resultado de ``frequencies_naive`` (``dict`` palavra -> ocorrências;
    a ordem das chaves é a da primeira aparição), em tempo linear."""
    raise NotImplementedError


def fib_naive(n):
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


def fib_fast(n):
    """Mesmo resultado de ``fib_naive``, instantâneo até ``n = 5000`` (cuidado
    com o limite de recursão: use um laço)."""
    raise NotImplementedError
