"""Gabarito do exercício 3."""


def count_eq_calls(n: int, hash_fn) -> int:
    calls = 0

    class Key:
        def __init__(self, value):
            self.value = value

        def __hash__(self):
            return hash_fn(self.value)

        def __eq__(self, other):
            nonlocal calls
            calls += 1
            return self.value == other.value

    table = {}
    for i in range(n):
        table[Key(i)] = i
    return calls
