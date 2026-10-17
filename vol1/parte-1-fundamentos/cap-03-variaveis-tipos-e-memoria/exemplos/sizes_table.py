"""Tamanho em bytes (getsizeof) de objetos comuns no CPython 3.15, 64 bits."""
import sys
from array import array
from decimal import Decimal
from fractions import Fraction

samples = {
    "None": None,
    "True": True,
    "int 0": 0,
    "int 2**30": 2**30,
    "int 2**100": 2**100,
    "float": 1.5,
    "complex": 1 + 2j,
    "Decimal": Decimal("1.1"),
    "Fraction": Fraction(1, 3),
    "str ''": "",
    "str 'abc'": "abc",
    "bytes b''": b"",
    "bytes(10)": bytes(10),
    "tuple ()": (),
    "tuple (1,2,3)": (1, 2, 3),
    "list []": [],
    "list [1,2,3]": [1, 2, 3],
    "dict {}": {},
    "dict {1:1}": {1: 1},
    "set()": set(),
    "frozenset()": frozenset(),
    "range(10**9)": range(10**9),
    "object()": object(),
    "array('q', 3 items)": array("q", [1, 2, 3]),
}
for name, obj in samples.items():
    print(f"{name:<22}{sys.getsizeof(obj):>6} bytes")
