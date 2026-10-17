"""Custo de um decorador: chamada direta x decorada."""
import functools
import timeit


def work(a, b):
    return a + b


def passthrough(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def passthrough_wraps(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def typed_passthrough(func):
    def wrapper(a, b):          # assinatura fixa, sem *args/**kwargs
        return func(a, b)
    return wrapper


plain = work
wrapped = passthrough(work)
wrapped_w = passthrough_wraps(work)
fixed = typed_passthrough(work)
cached = functools.lru_cache(maxsize=None)(work)
cached(1, 2)

N = 2_000_000
cases = {
    "direct": plain,
    "wrapper(*args, **kwargs)": wrapped,
    "same, with functools.wraps": wrapped_w,
    "wrapper(a, b)": fixed,
    "lru_cache (hit)": cached,
}
base = None
for name, fn in cases.items():
    best = min(timeit.repeat("fn(1, 2)", globals={"fn": fn},
                             number=N, repeat=5))
    ns = best / N * 1e9
    base = base or ns
    print(f"{name:28} {ns:6.1f} ns  (+{ns - base:5.1f})")

# O custo de DECORAR (uma vez) com e sem wraps
t_plain = min(timeit.repeat(lambda: passthrough(work),
                            number=100_000, repeat=5))
t_wraps = min(timeit.repeat(lambda: passthrough_wraps(work),
                            number=100_000, repeat=5))
print(f"decorating once: {t_plain / 1e5 * 1e9:.0f} ns "
      f"vs {t_wraps / 1e5 * 1e9:.0f} ns with wraps")
