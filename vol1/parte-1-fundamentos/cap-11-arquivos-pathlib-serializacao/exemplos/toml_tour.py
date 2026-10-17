"""tomllib: leitura de TOML (somente leitura, desde o 3.11)."""
import tomllib

text = """
title = "demo"
debug = false
port = 8080
ratio = 0.75
created = 2026-10-12T09:30:00-03:00

[database]
host = "localhost"
ports = [5432, 5433]

[[servers]]
name = "alpha"

[[servers]]
name = "beta"
"""

config = tomllib.loads(text)
print(config["database"]["ports"])
print([s["name"] for s in config["servers"]])
print(config["created"], type(config["created"]).__name__)
print(type(config["port"]).__name__, type(config["ratio"]).__name__)

# tomllib.load exige arquivo BINÁRIO (ele mesmo decodifica em UTF-8)
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="cap11_") as tmp:
    path = Path(tmp) / "app.toml"
    path.write_text(text, encoding="utf-8")
    with open(path, "rb") as f:
        print(tomllib.load(f)["title"])
    try:
        with open(path, encoding="utf-8") as f:
            tomllib.load(f)
    except TypeError as exc:
        print("TypeError:", exc)

try:
    tomllib.loads("a = 1\na = 2")
except tomllib.TOMLDecodeError as exc:
    print("TOMLDecodeError:", exc)

print(hasattr(tomllib, "dumps"))     # False: escrever exige terceiros
