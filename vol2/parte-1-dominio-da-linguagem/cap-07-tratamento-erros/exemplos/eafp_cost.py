"""EAFP x LBYL: o custo de try, de raise e das alternativas."""
import timeit

data = {"a": 1}


def no_try():
    x = 1
    return x


def with_try():
    try:
        x = 1
    except ValueError:
        pass
    return x


def raise_catch():
    try:
        raise ValueError
    except ValueError:
        pass


def get_miss_try():
    try:
        return data["z"]
    except KeyError:
        return None


def get_miss_get():
    return data.get("z")


def get_hit_try():
    try:
        return data["a"]
    except KeyError:
        return None


def get_hit_in():
    if "a" in data:
        return data["a"]
    return None


for func in (no_try, with_try, raise_catch, get_miss_try, get_miss_get,
             get_hit_try, get_hit_in):
    seconds = min(timeit.repeat(func, number=1_000_000, repeat=5)) / 1_000_000
    print(f"{func.__name__:<14}{seconds * 1e9:8.1f} ns")
