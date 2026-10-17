"""Gabarito do exercício 3."""


def sort_employees(employees: list[tuple[str, str, int]]) -> list[tuple[str, str, int]]:
    # A tupla da key é comparada elemento a elemento; -salary inverte só o salário
    return sorted(employees, key=lambda e: (e[1], -e[2], e[0]))
