"""Os degraus de tamanho do dict e do set, e um modelo que os explica."""
import sys

from dictpeek import inspect_dict, model_getsizeof


def dict_steps(make_key, limit=3000):
    d, last, steps = {}, sys.getsizeof({}), []
    steps.append((0, last))
    for n in range(1, limit + 1):
        d[make_key(n)] = n
        size = sys.getsizeof(d)
        if size != last:
            steps.append((n, size))
            last = size
    return steps


print("dict com chaves int (len, bytes):")
print(dict_steps(lambda n: n))
print("dict com chaves str:")
print(dict_steps(lambda n: f"k{n}"))

print("\nanatomia de cada degrau (chaves int):")
print("len  slots cabem  índice  entrada  bytes  modelo")
for n in (1, 6, 11, 22, 43, 86, 171, 342, 683, 1366, 2731):
    d = {i: i for i in range(n)}
    info = inspect_dict(d)
    cap = info["usable"] + info["nentries"]
    model = model_getsizeof(info["slots"], cap, info["entry_size"],
                            info["index_width"])
    print(f"{n:>4} {info['slots']:>5} {cap:>5} {info['index_width']:>6}"
          f" {info['entry_size']:>8} {sys.getsizeof(d):>6} {model:>7}")

# O modelo reproduz getsizeof em TODOS os tamanhos testados?
mismatch = 0
for make_key in (lambda n: n, lambda n: f"k{n}"):
    d = {}
    for n in range(1, 5000):
        d[make_key(n)] = n
        i = inspect_dict(d)
        cap = i["usable"] + i["nentries"]
        if model_getsizeof(i["slots"], cap, i["entry_size"],
                           i["index_width"]) != sys.getsizeof(d):
            mismatch += 1
print("\ndivergências do modelo em 2 x 4999 tamanhos:", mismatch)

# Uma chave que não é str "converte" a tabela inteira
mixed = {f"k{i}": i for i in range(5)}
print("5 chaves str:", sys.getsizeof(mixed))
mixed[1] = "int"
print("+ uma chave int:", sys.getsizeof(mixed))

# Set: degraus
s, last, steps = set(), sys.getsizeof(set()), []
steps.append((0, last))
for n in range(1, 200_000):
    s.add(n)
    size = sys.getsizeof(s)
    if size != last:
        steps.append((n, size))
        last = size
print("\nset (len, bytes):")
print(steps)
