"""Lendo o uv.lock deste projeto: o que está travado."""
import tomllib
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
packages = lock["package"]

print("formato:", lock["version"], "| requires-python:", lock["requires-python"], "| pacotes:", len(packages))
for package in packages:
    source = next(iter(package["source"]))
    wheels = package.get("wheels", [])
    with_hash = sum(1 for wheel in wheels if "hash" in wheel)
    print(f"  {package['name']:<36}{package['version']:<10}{source:<10}wheels com hash: {with_hash}")

print("fontes:", dict(Counter(next(iter(p["source"])) for p in packages)))
own = next(p for p in packages if p["name"] == "cap-02-gerenciamento-dependencias")
print("o próprio projeto:", own["source"], "| declara:", own["metadata"]["requires-dist"])
