"""Geradores infinitos e consumo parcial."""
from itertools import islice


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def naturals(start=0):
    n = start
    while True:
        yield n
        n += 1


print(list(islice(fibonacci(), 10)))
fib = fibonacci()
for value in fib:
    if value > 100:
        break
print(value, next(fib))      # o gerador continua de onde parou


def primes():
    found = []
    for n in naturals(2):
        if all(n % p for p in found if p * p <= n):
            found.append(n)
            yield n


print(list(islice(primes(), 10)))
print(next(x for x in primes() if x > 1000))
