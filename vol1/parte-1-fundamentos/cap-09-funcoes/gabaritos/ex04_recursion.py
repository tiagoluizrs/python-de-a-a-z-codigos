"""Gabarito do exercício 4."""


def fact_recursive(n):
    if n < 0:
        raise ValueError("n must be >= 0")
    return 1 if n <= 1 else n * fact_recursive(n - 1)


def fact_iterative(n):
    if n < 0:
        raise ValueError("n must be >= 0")
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


def fib_iterative(n):
    # só os dois últimos valores: O(n) de tempo, O(1) de espaço extra
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def measured_depth():
    depth = 0

    def dive():
        nonlocal depth
        depth += 1
        dive()

    try:
        dive()
    except RecursionError:
        return depth
