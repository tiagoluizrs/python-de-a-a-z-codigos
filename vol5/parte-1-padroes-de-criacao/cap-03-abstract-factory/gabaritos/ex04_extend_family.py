"""Gabarito do exercício 4."""


def extend_families(families, product, builders):
    if any(product in family for family in families.values()):
        raise ValueError(f"produto já existe: {product!r}")
    missing = sorted(set(families) - set(builders))
    if missing:
        raise ValueError(f"faltam construtores para: {', '.join(missing)}")
    unknown = sorted(set(builders) - set(families))
    if unknown:
        raise ValueError(f"famílias desconhecidas: {', '.join(unknown)}")
    return {name: {**family, product: builders[name]} for name, family in families.items()}


def add_family(families, name, products, *, like=None):
    if name in families:
        raise ValueError(f"família já existe: {name!r}")
    if like is not None and like not in families:
        raise KeyError(like)
    reference_name = like if like is not None else next(iter(families), None)
    if reference_name is not None:
        reference = set(families[reference_name])
        have = set(products)
        parts = []
        if reference - have:
            parts.append("faltam " + ", ".join(sorted(reference - have)))
        if have - reference:
            parts.append("sobram " + ", ".join(sorted(have - reference)))
        if parts:
            raise ValueError("produtos incompatíveis: " + "; ".join(parts))
    return {**{k: dict(v) for k, v in families.items()}, name: dict(products)}
