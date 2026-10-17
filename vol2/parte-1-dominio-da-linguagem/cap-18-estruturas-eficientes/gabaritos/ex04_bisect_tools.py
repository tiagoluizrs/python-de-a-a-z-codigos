"""Gabarito do exercício 4."""
import bisect


def grade(score, breakpoints, labels):
    return labels[bisect.bisect(breakpoints, score)]


def insert_unique(sorted_list, value):
    index = bisect.bisect_left(sorted_list, value)
    if index < len(sorted_list) and sorted_list[index] == value:
        return False
    sorted_list.insert(index, value)
    return True


def count_in_range(sorted_list, low, high):
    return max(0, bisect.bisect_right(sorted_list, high) - bisect.bisect_left(sorted_list, low))


def closest(sorted_list, target):
    if not sorted_list:
        raise ValueError("lista vazia")
    index = bisect.bisect_left(sorted_list, target)
    candidates = sorted_list[max(0, index - 1):index + 1]
    return min(candidates, key=lambda value: (abs(value - target), value))
