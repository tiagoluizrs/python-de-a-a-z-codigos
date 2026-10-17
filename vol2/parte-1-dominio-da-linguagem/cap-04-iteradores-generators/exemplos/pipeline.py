"""Pipeline de geradores: nada e materializado."""
from itertools import islice


def read_numbers(n):
    for i in range(n):
        print(f"  ler {i}")
        yield i


def square(items):
    for x in items:
        print(f"  elevar {x}")
        yield x * x


def only_odd(items):
    for x in items:
        if x % 2:
            yield x


print("-- primeiros 2 impares ao quadrado")
pipe = only_odd(square(read_numbers(10**9)))
print(list(islice(pipe, 2)))
