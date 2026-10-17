"""Arquivos de configuração: TOML, INI e JSON, o mesmo conteúdo, três comportamentos."""
import configparser
import json
import tempfile
import time
import tomllib
from pathlib import Path

TOML = """
debug = false
port = 8080
hosts = ["a.example.com", "b.example.com"]

[database]
url = "postgresql://localhost/app"
pool = 5
timeout = 2.5
"""

INI = """
[app]
debug = false
port = 8080

[database]
url = postgresql://localhost/app
pool = 5
timeout = 2.5
"""

JSON = json.dumps({"debug": False, "port": 8080, "hosts": ["a.example.com", "b.example.com"],
                   "database": {"url": "postgresql://localhost/app", "pool": 5, "timeout": 2.5}})

data = tomllib.loads(TOML)
print("TOML -> tipos preservados:", {k: type(v).__name__ for k, v in data.items()}, "| pool:", type(data["database"]["pool"]).__name__)

parser = configparser.ConfigParser()
parser.read_string(INI)
print("INI  -> tudo é str:", repr(parser["database"]["pool"]), "| conversão explícita:", parser["database"].getint("pool"), parser["app"].getboolean("debug"))
print("JSON -> tipos preservados, mas sem comentários e sem vírgula final:", json.loads(JSON)["database"]["timeout"])

# Erros com localização
try:
    tomllib.loads("port = 8080\nhosts = [\n  'a',\n  'b' 'c'\n]\n")
except tomllib.TOMLDecodeError as error:
    print("TOMLDecodeError:", error)

# tomllib lê, mas NÃO escreve
print("tomllib.dumps existe?", hasattr(tomllib, "dumps"))

# Custo de ler um arquivo grande (2.000 chaves)
big_toml = "\n".join(f"key{i} = {i}" for i in range(2000))
big_json = json.dumps({f"key{i}": i for i in range(2000)})
big_ini = "[s]\n" + "\n".join(f"key{i} = {i}" for i in range(2000))


def ini_parse():
    parser = configparser.ConfigParser()
    parser.read_string(big_ini)


for label, fn in [("tomllib", lambda: tomllib.loads(big_toml)), ("json", lambda: json.loads(big_json)), ("configparser", ini_parse)]:
    best = float("inf")
    for _ in range(5):
        start = time.perf_counter()
        for _ in range(20):
            fn()
        best = min(best, (time.perf_counter() - start) / 20)
    print(f"  ler 2.000 chaves com {label:<13}{best * 1e3:6.2f} ms")
