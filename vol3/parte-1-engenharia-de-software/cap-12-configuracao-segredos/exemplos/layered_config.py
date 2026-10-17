"""Camadas: padrões < arquivo < ambiente < linha de comando, e de onde veio cada valor."""
import argparse
import os
import tomllib
from collections import ChainMap
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    debug: bool
    workers: int


DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "workers": 2}
FILE = tomllib.loads('host = "0.0.0.0"\nworkers = 4\n')
ENV = {"port": 9000, "debug": True}                                       # já convertidos (APP_PORT=9000, APP_DEBUG=1)
CLI = {"workers": 8}


def load(layers):
    merged = ChainMap(*layers)                                             # a PRIMEIRA camada vence
    return Settings(**{field: merged[field] for field in DEFAULTS})


settings = load([CLI, ENV, FILE, DEFAULTS])
print(settings)

# De onde veio cada valor? (proveniência)
names = ["linha de comando", "ambiente", "arquivo", "padrão"]
for field in DEFAULTS:
    for name, layer in zip(names, [CLI, ENV, FILE, DEFAULTS]):
        if field in layer:
            print(f"  {field:<8}= {getattr(settings, field)!r:<12} <- {name}")
            break

# O mesmo, com argparse + variáveis de ambiente reais
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", DEFAULTS["port"])))
parser.add_argument("--workers", type=int, default=int(os.environ.get("APP_WORKERS", DEFAULTS["workers"])))
os.environ["APP_PORT"] = "7000"
print("\nargparse com default vindo do ambiente (lido na criação do parser):", parser.parse_args([]).port, "| e --port 1:", parser.parse_args(["--port", "1"]).port)

# Fail fast: valide TUDO na partida, com uma mensagem completa
def validate(raw):
    problems = []
    if not 1 <= raw["port"] <= 65535:
        problems.append(f"port fora de 1..65535: {raw['port']}")
    if raw["workers"] < 1:
        problems.append(f"workers deve ser >= 1: {raw['workers']}")
    if problems:
        raise SystemExit("configuração inválida:\n  " + "\n  ".join(problems))
    return raw


try:
    validate({"port": 70000, "workers": 0})
except SystemExit as error:
    print(error)
