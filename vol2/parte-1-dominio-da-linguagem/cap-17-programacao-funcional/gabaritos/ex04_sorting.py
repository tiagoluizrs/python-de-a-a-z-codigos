"""Gabarito do exercício 4."""
from functools import cmp_to_key
from operator import itemgetter


def sort_by(records, *keys):
    result = list(records)
    for key in reversed(keys):                      # critério menos importante primeiro
        descending = key.startswith("-")
        name = key[1:] if descending else key
        result.sort(key=itemgetter(name), reverse=descending)
    return result


def sort_numbers_largest(numbers):
    def compare(a, b):
        return (a + b < b + a) - (a + b > b + a)    # a antes de b se a+b for maior

    return "".join(sorted(map(str, numbers), key=cmp_to_key(compare)))
