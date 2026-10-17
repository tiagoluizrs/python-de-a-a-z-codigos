"""Gabarito do exercício 5."""
import sys


def caller_names():
    names = []
    frame = sys._getframe(1)
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def recursion_capacity():
    def probe(n):
        try:
            return probe(n + 1)
        except RecursionError:
            return n

    return probe(0)


def calling_line():
    return sys._getframe(1).f_lineno
