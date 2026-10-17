"""traceback, tracemalloc, warnings, doctest, timeit, reprlib, pprint."""
import doctest
import pprint
import reprlib
import timeit
import traceback
import tracemalloc
import warnings


def add(a, b):
    """Soma dois valores.

    >>> add(2, 3)
    5
    """
    return a + b


print(doctest.testmod())

try:
    1 / 0
except ZeroDivisionError:
    print(traceback.format_exc().splitlines()[-1])

tracemalloc.start()
data = [str(i) for i in range(10_000)]
cur, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(cur > 100_000, peak >= cur)

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    warnings.warn("old api", DeprecationWarning)
print(caught[0].category.__name__, caught[0].message)

print(reprlib.repr(list(range(100))))
pprint.pp({"a": list(range(30)), "b": {"c": 1}}, width=40, compact=True)
print(timeit.timeit("sum(range(100))", number=10_000) > 0)
