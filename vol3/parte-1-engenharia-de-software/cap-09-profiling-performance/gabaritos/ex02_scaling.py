"""Gabarito do exercício 2."""
import math
import time


def estimate_exponent(sizes, times):
    if len(sizes) != len(times) or len(sizes) < 2 or any(s <= 0 for s in sizes) or any(t <= 0 for t in times):
        raise ValueError("são necessários pelo menos 2 pontos positivos")
    xs, ys = [math.log(s) for s in sizes], [math.log(t) for t in times]
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("tamanhos iguais")
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator


def classify(exponent):
    if exponent < 0.3:
        return "constante"
    if exponent < 1.4:
        return "linear"
    if exponent < 2.4:
        return "quadrática"
    return "cúbica ou pior"


def measure_scaling(func, make_input, sizes, repeat=3, clock=time.perf_counter):
    times = []
    for n in sizes:
        data = make_input(n)
        best = float("inf")
        for _ in range(repeat):
            start = clock()
            func(data)
            best = min(best, clock() - start)
        times.append(best)
    return estimate_exponent(sizes, times), times
