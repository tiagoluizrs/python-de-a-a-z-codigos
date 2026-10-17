"""Exercício 3: memoização manual com dict (gabarito)."""


def memoize(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            wrapper.hits += 1
            return cache[args]
        wrapper.misses += 1
        cache[args] = func(*args)
        return cache[args]

    # atributos pendurados na própria função
    wrapper.cache = cache
    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


def count_calls_fib(n):
    calls = 0
    memo = {}

    def fib(k):
        nonlocal calls
        calls += 1
        if k < 2:
            return k
        if k not in memo:
            memo[k] = fib(k - 1) + fib(k - 2)
        return memo[k]

    value = fib(n)
    return value, calls
