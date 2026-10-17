"""Gabarito do exercício 4."""


def by_family(catalog):
    result: dict[str, list[str]] = {}
    for p in catalog:
        result.setdefault(p["family"], []).append(p["name"])
    return result


def verdict_counts(catalog):
    counts: dict[str, int] = {}
    for p in catalog:
        counts[p["verdict"]] = counts.get(p["verdict"], 0) + 1
    return dict(sorted(counts.items()))


def embedded(catalog):
    return sorted(p["name"] for p in catalog if p["verdict"] == "embutido")


def chapters_of(catalog, *names):
    index = {p["name"].lower(): p["chapter"] for p in catalog}
    out = []
    for name in names:
        if name.lower() not in index:
            raise KeyError(name)
        out.append(index[name.lower()])
    return out


def missing_chapters(catalog, extras, first, last):
    covered = {p["chapter"] for p in catalog} | {e["chapter"] for e in extras}
    return [c for c in range(first, last + 1) if c not in covered]


def python_share(catalog):
    if not catalog:
        raise ValueError("catálogo vazio")
    return round(sum(p["verdict"] in ("embutido", "simplificado") for p in catalog) / len(catalog), 2)
