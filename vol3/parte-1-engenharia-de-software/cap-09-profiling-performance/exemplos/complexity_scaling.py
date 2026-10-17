"""Complexidade na prática: medir como o tempo CRESCE com n (inclinação em escala log-log)."""
import math
import random
import time


def measure(func, n, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        args = func.prepare(n)
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best


def slope(sizes, times):
    xs, ys = [math.log(s) for s in sizes], [math.log(t) for t in times]
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)


def case(prepare):
    def wrap(func):
        func.prepare = prepare
        return func
    return wrap


@case(lambda n: (list(range(n)), -1))
def list_membership(data, needle):           # O(n): varre tudo (20 buscas, para o tempo ficar mensurável)
    for _ in range(20):
        needle in data


@case(lambda n: (set(range(n)), -1))
def set_membership(data, needle):            # O(1) (20 mil buscas pelo mesmo motivo)
    for _ in range(20_000):
        needle in data


@case(lambda n: (random.sample(range(n), n),))
def sort_list(data):                         # O(n log n)
    return sorted(data)


@case(lambda n: (list(range(n)),))
def quadratic_pairs(data):                   # O(n^2): todos os pares
    count = 0
    for a in data:
        for b in data:
            if a < b:
                count += 1
    return count


@case(lambda n: (list(range(n)),))
def linear_sum(data):                        # O(n)
    return sum(x * 2 for x in data)


print(f"{'operação':<18}{'inclinação':>11}   leitura")
for func, sizes in [(list_membership, [20_000, 40_000, 80_000, 160_000]), (set_membership, [20_000, 80_000, 320_000, 1_280_000]),
                    (sort_list, [20_000, 40_000, 80_000, 160_000]), (quadratic_pairs, [300, 600, 1_200, 2_400]),
                    (linear_sum, [50_000, 100_000, 200_000, 400_000])]:
    times = [measure(func, n) for n in sizes]
    k = slope(sizes, times)
    reading = "constante" if k < 0.3 else "linear (ou n log n)" if k < 1.4 else "quadrático"
    print(f"{func.__name__:<18}{k:>11.2f}   {reading}")
