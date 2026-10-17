"""Detalhes internos: o prefixo ``_`` avisa que não faz parte da API pública."""


def normalize_sku(sku):
    return sku.strip().upper()
