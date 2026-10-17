"""Custo medido do deepcopy e de suas alternativas."""
import copy
import json
import pickle
import timeit
import tracemalloc

SIZE = 10_000
data = [
    {"id": i, "name": f"user-{i}", "tags": ["a", "b", "c"],
     "pos": (i, i + 1)}
    for i in range(SIZE)
]


def per_call(fn, number=20):
    best = min(timeit.repeat(fn, number=number, repeat=5))
    return best / number * 1000   # ms por chamada


def rebuild(rows):
    return [{**r, "tags": list(r["tags"])} for r in rows]


candidates = {
    "list(data)  (rasa)": lambda: list(data),
    "copy.copy   (rasa)": lambda: copy.copy(data),
    "rebuild manual    ": lambda: rebuild(data),
    "pickle roundtrip  ": lambda: pickle.loads(pickle.dumps(data)),
    "json roundtrip    ": lambda: json.loads(json.dumps(
        [{**r, "pos": list(r["pos"])} for r in data])),
    "copy.deepcopy     ": lambda: copy.deepcopy(data),
}

print(f"{SIZE} dicts, cada um com lista e tupla")
for label, fn in candidates.items():
    print(f"{label} {per_call(fn):8.2f} ms")

print()
for label in ("copy.copy   (rasa)", "rebuild manual    ",
              "copy.deepcopy     "):
    tracemalloc.start()
    result = candidates[label]()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{label} memória nova: {current / 1e6:6.2f} MB "
          f"(pico {peak / 1e6:.2f} MB)")
    del result
