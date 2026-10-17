"""Gabarito do exercício 4."""


def coalesce(*values, default=None):
    for value in values:
        if value is not None:        # 'is not None', e NÃO a veracidade do valor
            return value
    return default
