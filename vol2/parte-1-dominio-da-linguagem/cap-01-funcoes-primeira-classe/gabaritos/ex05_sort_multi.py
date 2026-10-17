"""Exercício 5: ordenar por vários critérios com itemgetter (gabarito)."""
from operator import itemgetter


def sort_staff(rows):
    result = list(rows)                      # cópia: não altera a entrada
    # ordenação estável: do critério menos importante ao mais importante
    result.sort(key=itemgetter("name"))
    result.sort(key=itemgetter("salary"), reverse=True)
    result.sort(key=itemgetter("dept"))
    return result


def top_per_dept(rows):
    top = {}
    # já ordenado: o primeiro de cada dept é o de maior salário
    for row in sort_staff(rows):
        top.setdefault(row["dept"], row["name"])
    return top
