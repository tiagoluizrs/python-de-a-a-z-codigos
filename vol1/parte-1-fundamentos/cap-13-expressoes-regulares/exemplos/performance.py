"""Medições: compile, cache, str x regex, in x search."""
import re
import timeit

TEXT = "order 12345 shipped to Sao Paulo on 2026-10-12"
DATE = r"\d{4}-\d{2}-\d{2}"
PAT = re.compile(DATE)


def ns(func, number=200_000) -> float:
    """Melhor de 5 repetições, em ns por chamada."""
    return min(timeit.repeat(func, number=number, repeat=5)) / number * 1e9


def cold_compile():
    re.purge()
    return re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\s+\w+")


def main() -> None:
    print("-- compile e cache")
    print("re.search(str):", round(ns(lambda: re.search(DATE, TEXT))), "ns")
    print("pat.search    :", round(ns(lambda: PAT.search(TEXT))), "ns")
    print("re.compile(hit):", round(ns(lambda: re.compile(DATE))), "ns")
    cold = min(timeit.repeat(cold_compile, number=1000, repeat=5)) / 1000
    print("compilação a frio:", round(cold * 1e6, 1), "us")

    print("-- str x regex (mesma tarefa, padrão já compilado)")
    cases = {
        "startswith": (lambda: TEXT.startswith("order"),
                       re.compile("order").match),
        "contains": (lambda: "shipped" in TEXT,
                     re.compile("shipped").search),
        "replace": (lambda: TEXT.replace("Sao Paulo", "SP"),
                    lambda t: re.compile("Sao Paulo").sub("SP", t)),
        "split": (lambda: TEXT.split(" "), re.compile(" ").split),
    }
    for name, (str_fn, re_fn) in cases.items():
        if name == "replace":
            sub = re.compile("Sao Paulo").sub
            re_call = lambda: sub("SP", TEXT)
        else:
            re_call = lambda f=re_fn: f(TEXT)
        a, b = ns(str_fn), ns(re_call)
        print(f"{name:<11} str {a:5.0f} ns  regex {b:5.0f} ns  x{b / a:.1f}")

    print("-- in x search em texto grande")
    base = "lorem ipsum " * 50_000
    for needle in ("needle", "ipsum X"):
        big = base + needle
        pn = re.compile(needle)
        t_in = ns(lambda: needle in big, 100)
        t_re = ns(lambda: pn.search(big), 100)
        print(f"{needle!r}: {len(big)} chars: in {t_in / 1e3:.0f} us, "
              f"search {t_re / 1e3:.0f} us")


if __name__ == "__main__":
    main()
