"""Lendo o pyproject.toml deste projeto com a biblioteca padrão."""
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
with open(root / "pyproject.toml", "rb") as handle:           # tomllib exige modo binário
    config = tomllib.load(handle)

print(list(config))
print(config["project"]["name"], config["project"]["version"], config["project"]["requires-python"])
print(config["project"]["scripts"])
print(config["dependency-groups"])
print(config["build-system"]["build-backend"], config["tool"]["uv"]["build-backend"])

try:
    tomllib.loads("name = ")
except tomllib.TOMLDecodeError as error:
    print("TOMLDecodeError:", error)
