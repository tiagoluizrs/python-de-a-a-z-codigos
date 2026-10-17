"""Muitos ramos: o ultimo ramo de 20 em if, match e dict."""
import timeit

N = 20
names = [f"op{i}" for i in range(N)]

src_if = "def f(x):\n"
src_if += "".join(
    f"    {'if' if i == 0 else 'elif'} x == 'op{i}': return {i}\n"
    for i in range(N))
src_match = "def f(x):\n    match x:\n" + "".join(
    f"        case 'op{i}': return {i}\n" for i in range(N))
src_dict = ("T = {" + ", ".join(f"'op{i}': {i}" for i in range(N))
            + "}\ndef f(x): return T[x]\n")

for label, src in (("if/elif", src_if), ("match", src_match),
                   ("dict", src_dict)):
    ns = {}
    exec(src, ns)
    f = ns["f"]
    for key in ("op0", "op19"):
        n = 500_000
        best = min(timeit.repeat(lambda: f(key), number=n, repeat=5))
        print(f"{label:8} {key:5} {best / n * 1e9:6.1f} ns")
