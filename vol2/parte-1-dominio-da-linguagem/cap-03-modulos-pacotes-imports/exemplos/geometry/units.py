"""Fatores de conversão lidos de um arquivo de dados do pacote."""
import json
from importlib import resources

# Lê "data/units.json" de dentro do pacote, onde quer que ele esteja.
_text = (resources.files("geometry") / "data" / "units.json").read_text("utf-8")
_FACTORS = json.loads(_text)


def factor(unit: str) -> float:
    return _FACTORS[unit]
