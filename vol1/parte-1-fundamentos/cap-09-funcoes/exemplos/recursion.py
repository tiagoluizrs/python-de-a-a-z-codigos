"""Recursão, limite e iteração."""
import sys
import time


def fact_rec(n):
    return 1 if n <= 1 else n * fact_rec(n - 1)


def fact_iter(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


print(sys.getrecursionlimit())
try:
    fact_rec(5000)
except RecursionError as exc:
    print("RecursionError:", exc)


def depth():
    count = 0

    def go():
        nonlocal count
        count += 1
        go()

    try:
        go()
    except RecursionError:
        return count

print(depth())
sys.setrecursionlimit(20_000)
print(fact_rec(5000) == fact_iter(5000))
print(depth())
sys.setrecursionlimit(1000)

for fn in (fact_rec, fact_iter):
    t = time.perf_counter()
    for _ in range(200):
        fn(900)
    print(fn.__name__, f"{(time.perf_counter() - t) / 200 * 1e6:.0f} us")


def fib_naive(n):
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)

calls = 0
def fib_count(n):
    global calls
    calls += 1
    return n if n < 2 else fib_count(n - 1) + fib_count(n - 2)

fib_count(25)
print(calls)
