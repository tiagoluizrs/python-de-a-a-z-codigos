"""A árvore de dependências do ambiente atual (importlib.metadata + marcadores)."""
import re
from importlib import metadata

from packaging.markers import Marker


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def direct_requirements(dist_name):
    """Dependências de execução (ignora extras opcionais)."""
    result = []
    for line in metadata.requires(dist_name) or []:
        requirement, _, marker = line.partition(";")
        if marker and (not Marker(marker).evaluate({"extra": ""})):
            continue                                         # marcador falso neste ambiente (inclui extras)
        name = re.split(r"[ \[<>=!~(]", requirement.strip(), maxsplit=1)[0]
        result.append(normalize(name))
    return sorted(set(result))


def print_tree(name, prefix="", seen=()):
    for index, dep in enumerate(direct_requirements(name)):
        last = index == len(direct_requirements(name)) - 1
        try:
            version = metadata.version(dep)
        except metadata.PackageNotFoundError:
            print(f"{prefix}{'└── ' if last else '├── '}{dep} (não instalado neste ambiente)")
            continue
        print(f"{prefix}{'└── ' if last else '├── '}{dep} {version}")
        if dep not in seen:
            print_tree(dep, prefix + ("    " if last else "│   "), (*seen, dep))


print("pytest", metadata.version("pytest"))
print_tree("pytest")

# Quem depende de quê (inverso): quantos pacotes instalados exigem 'packaging'?
users = sorted(d.metadata["Name"] for d in metadata.distributions() if "packaging" in direct_requirements(d.metadata["Name"]))
print("exigem packaging:", users)
