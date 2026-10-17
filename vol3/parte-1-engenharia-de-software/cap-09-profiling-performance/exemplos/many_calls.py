"""Muitas chamadas pequenas: o pior caso para um profiler determinístico."""


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    print(fib(32))
