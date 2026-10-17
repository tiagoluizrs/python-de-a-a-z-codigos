"""Compreensões de dict, inversão, aninhamento, cópia."""
import copy

squares = {n: n * n for n in range(5)}
print(squares)
prices = {"apple": 3.5, "pear": 5.0, "fig": 12.0}
cheap = {k: v for k, v in prices.items() if v < 10}
print(cheap)
print({k.upper(): v for k, v in prices.items()})

# Inversão ingênua perde dados quando valores se repetem
grades = {"Ana": "A", "Bia": "B", "Caio": "A"}
print({v: k for k, v in grades.items()})   # perdeu Ana!

# Chave duplicada em literal: a última vence
print({"a": 1, "a": 2})

# Aninhados e cópia rasa x profunda
config = {"db": {"host": "x", "port": 1}, "tags": ["a"]}
shallow = config.copy()
deep = copy.deepcopy(config)
config["db"]["port"] = 2
config["tags"].append("b")
print(shallow["db"], shallow["tags"])
print(deep["db"], deep["tags"])
print(dict(config) is config, {**config} == config)

# Acesso seguro a aninhados
data = {"user": {"address": {"city": "Recife"}}}
print(data.get("user", {}).get("address", {}).get("zip", "?"))
