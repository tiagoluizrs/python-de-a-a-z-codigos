"""JSON: mapeamento de tipos, opções de dumps e armadilhas."""
import json
import math

# --- mapeamento Python <-> JSON
data = {"name": "Ana", "age": 31, "vip": True, "city": "São Paulo"}
text = json.dumps(data)
print(text)
print(json.loads(text) == data)
print(json.dumps([1, 2.5, None, False, "x"]))

# --- opções de dumps
print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
print(json.dumps(data, separators=(",", ":")))   # compacto
print(json.dumps("ação"), json.dumps("ação", ensure_ascii=False))

# --- armadilha 1: chaves viram str
d = {1: "a", 2.5: "b", None: "c", False: "d"}
print(json.dumps(d))
print(json.loads(json.dumps({1: "a"})))          # {'1': 'a'}

# --- armadilha 2: tupla vira lista; conjunto não serializa
print(json.loads(json.dumps({"point": (1, 2)})))
try:
    json.dumps({"tags": {"a", "b"}})
except TypeError as exc:
    print("TypeError:", exc)

# --- armadilha 3: NaN e Infinity não são JSON válido
print(json.dumps([math.nan, math.inf]))
try:
    json.dumps(math.nan, allow_nan=False)
except ValueError as exc:
    print("ValueError:", exc)

# --- armadilha 4: inteiros grandes e floats
big = 2**70
print(json.loads(json.dumps(big)) == big)        # Python preserva
print(json.dumps(0.1 + 0.2))                     # 0.30000000000000004
print(json.loads("1e3"), json.loads("10"))       # 1000.0 10

# --- armadilha 5: chaves duplicadas, a última vence
print(json.loads('{"a": 1, "a": 2}'))

# --- erro de sintaxe
try:
    json.loads("{'a': 1}")
except json.JSONDecodeError as exc:
    print("JSONDecodeError:", exc.msg, exc.lineno, exc.colno)

# --- parse_float: Decimal sem perda
from decimal import Decimal
print(json.loads('{"price": 19.90}', parse_float=Decimal))

# --- array_hook (novo no 3.15): listas JSON viram tuplas
print(json.loads('{"p": [1, [2, 3]]}', array_hook=tuple))
