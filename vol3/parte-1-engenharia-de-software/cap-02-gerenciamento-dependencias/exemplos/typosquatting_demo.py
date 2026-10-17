"""Nomes parecidos: o ataque de typosquatting e uma checagem simples."""
import difflib

POPULAR = ["requests", "numpy", "pandas", "django", "flask", "pytest", "urllib3", "cryptography"]


def distance(a, b):
    """Distância de edição (Levenshtein), em O(len(a) * len(b))."""
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


for candidate in ["requests", "reqeusts", "request", "nunpy", "djanga", "pandas-utils", "colorama"]:
    close = [(p, distance(candidate, p)) for p in POPULAR if 0 < distance(candidate, p) <= 2]
    print(f"{candidate:<14}", close or "ok (sem nome popular parecido)")
print(difflib.get_close_matches("reqeusts", POPULAR, n=2, cutoff=0.8))
