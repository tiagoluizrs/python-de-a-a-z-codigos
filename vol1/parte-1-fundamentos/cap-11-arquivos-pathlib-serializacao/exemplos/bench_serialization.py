"""json x pickle: tempo e tamanho para o mesmo objeto."""
import json
import pickle
import timeit

records = [
    {"id": i, "name": f"user-{i}", "score": i * 0.37,
     "tags": ["a", "b", "c"], "active": i % 2 == 0}
    for i in range(50_000)
]


def best_ms(func, repeat=5):
    return min(timeit.repeat(func, number=1, repeat=repeat)) * 1000


json_text = json.dumps(records)
pickle_blob = pickle.dumps(records)

print(f"{'':18}{'bytes':>10}{'dumps ms':>10}{'loads ms':>10}")
print(f"{'json':18}{len(json_text.encode()):>10}"
      f"{best_ms(lambda: json.dumps(records)):>10.1f}"
      f"{best_ms(lambda: json.loads(json_text)):>10.1f}")
print(f"{'pickle':18}{len(pickle_blob):>10}"
      f"{best_ms(lambda: pickle.dumps(records)):>10.1f}"
      f"{best_ms(lambda: pickle.loads(pickle_blob)):>10.1f}")
