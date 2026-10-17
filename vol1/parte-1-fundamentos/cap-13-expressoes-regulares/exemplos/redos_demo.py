"""ReDoS: backtracking catastrófico medido com entradas pequenas."""
import re
import time

EVIL = re.compile(r"(a+)+$")
ATOMIC = re.compile(r"(?>a+)+$")
REWRITTEN = re.compile(r"a+$")


def timed(pattern: re.Pattern, text: str, method="search") -> float:
    start = time.perf_counter()
    getattr(pattern, method)(text)
    return time.perf_counter() - start


def main() -> None:
    print("-- exponencial: n letras 'a' seguidas de '!'")
    print("n   evil(s)   atomico(s)  reescrito(s)")
    for n in range(16, 25, 2):
        text = "a" * n + "!"
        print(f"{n:<3} {timed(EVIL, text):<9.4f} "
              f"{timed(ATOMIC, text):<11.6f} "
              f"{timed(REWRITTEN, text):.6f}")

    print("-- search tenta cada posição inicial: quadrático")
    for n in (5_000, 10_000, 20_000, 40_000):
        text = "a" * n + "!"
        print(f"{n:<6} search {timed(REWRITTEN, text):.4f}s   "
              f"fullmatch {timed(REWRITTEN, text, 'fullmatch'):.6f}s")


if __name__ == "__main__":
    main()
