import struct
import sys


def test_deep_size(load_exercise):
    deep_size = load_exercise("ex01_deep_size").deep_size
    assert deep_size("abc") == sys.getsizeof("abc")
    big = "x" * 1000
    shared = [big, big, big]
    assert deep_size(shared) == sys.getsizeof(shared) + sys.getsizeof(big)
    data = {"k" * 50: ["v" * 60, (1.5, 2.5)]}
    assert deep_size(data) > sys.getsizeof(data) + 100


def test_deep_size_handles_cycles(load_exercise):
    deep_size = load_exercise("ex01_deep_size").deep_size
    loop = []
    loop.append(loop)
    assert deep_size(loop) == sys.getsizeof(loop)


def test_float_bits(load_exercise):
    float_bits = load_exercise("ex02_float_bits").float_bits
    assert float_bits(-2.0) == (1, 1024, 0)
    assert float_bits(1.0) == (0, 1023, 0)
    assert float_bits(0.1) == (0, 1019, 0x999999999999A)
    for value in (3.14, -1e-300, 1e300):
        sign, exp, mant = float_bits(value)
        packed = (sign << 63) | (exp << 52) | mant
        assert struct.pack(">Q", packed) == struct.pack(">d", value)


def test_predicted_int_size(load_exercise):
    predicted = load_exercise("ex03_int_size").predicted_int_size
    for n in (0, 1, -1, 255, 2**30 - 1, 2**30, 2**60, -(2**90), 10**100, 2**1000):
        assert predicted(n) == sys.getsizeof(n), n


def test_predicted_str_size(load_exercise):
    predicted = load_exercise("ex04_str_size").predicted_str_size
    for text in ("ab", "a" * 10, "é" * 10, "你" * 10, "😀" * 10, "a" * 999 + "😀"):
        assert predicted(text) == sys.getsizeof(text), text[:5]


def test_make_grid(load_exercise):
    make_grid = load_exercise("ex05_grid").make_grid
    grid = make_grid(2, 3)
    assert grid == [[0, 0, 0], [0, 0, 0]]
    grid[0][0] = 9
    assert grid[1][0] == 0
    assert grid[0] is not grid[1]
