"""Gabarito do exercício 5."""
import operator
from functools import reduce


def merge_dicts(*dicts):
    return reduce(operator.or_, dicts, {})


def deep_get(data, path, default=None):
    try:
        return reduce(operator.getitem, path, data)
    except (KeyError, IndexError, TypeError):
        return default


def product(numbers):
    return reduce(operator.mul, numbers, 1)


def group_by(items, key):
    def add(groups, item):
        groups.setdefault(key(item), []).append(item)
        return groups

    return reduce(add, items, {})
