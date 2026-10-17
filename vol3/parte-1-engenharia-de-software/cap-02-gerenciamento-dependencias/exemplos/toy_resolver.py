"""Um resolvedor de dependências minúsculo: escolher versões compatíveis."""
from packaging.specifiers import SpecifierSet
from packaging.version import Version

# índice: pacote -> versão -> {dependência: especificador}
INDEX = {
    "app": {"1.0": {"web": ">=2", "db": ">=1"}},
    "web": {"3.0": {"core": ">=2,<3"}, "2.0": {"core": ">=1,<3"}},
    "db": {"1.1": {"core": "<2"}, "1.0": {"core": "<2"}},
    "core": {"3.0": {}, "2.5": {}, "2.0": {}, "1.9": {}},
}


class ResolutionError(Exception):
    pass


def resolve(index, requirements, chosen=None):
    """Busca com retrocesso: tenta a versão mais nova de cada pacote."""
    chosen = dict(chosen or {})
    pending = dict(requirements)
    if not pending:
        return chosen
    name = sorted(pending)[0]
    spec = SpecifierSet(pending.pop(name))
    if name in chosen:                                       # já escolhido: só confere
        if Version(chosen[name]) in spec:
            return resolve(index, pending, chosen)
        raise ResolutionError(f"{name} {chosen[name]} não satisfaz {spec}")
    candidates = sorted((v for v in index.get(name, {}) if Version(v) in spec), key=Version, reverse=True)
    for version in candidates:
        merged = dict(pending)
        conflict = False
        for dep, dep_spec in index[name][version].items():
            if dep in merged:
                merged[dep] = f"{merged[dep]},{dep_spec}"            # une as restrições
            else:
                merged[dep] = dep_spec
            if dep in chosen and Version(chosen[dep]) not in SpecifierSet(merged[dep]):
                conflict = True
        if conflict:
            continue
        try:
            return resolve(index, merged, {**chosen, name: version})
        except ResolutionError:
            continue                                         # retrocede: tenta uma versão mais antiga
    raise ResolutionError(f"nenhuma versão de {name} satisfaz {spec}")


print(resolve(INDEX, {"app": ">=1"}))        # web 3.0 exige core>=2 e db exige core<2: conflito; retrocede para web 2.0
try:
    resolve(INDEX, {"app": ">=1", "core": ">=3"})
except ResolutionError as error:
    print("ResolutionError:", error)
