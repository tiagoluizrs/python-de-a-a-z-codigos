"""Compara o mesmo cálculo escrito em Python puro e delegado a código em C."""
import timeit

N = 10_000_000


def pure_python_loop():
    total = 0
    for number in range(N):
        total += number
    return total


def builtin_sum():
    # sum() é implementada em C: o laço roda fora do bytecode
    return sum(range(N))


assert pure_python_loop() == builtin_sum()

for func in (pure_python_loop, builtin_sum):
    seconds = min(timeit.repeat(func, number=1, repeat=5))
    print(f"{func.__name__:<18} {seconds:.3f} s")
