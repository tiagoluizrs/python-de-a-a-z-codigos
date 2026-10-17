import itertools
import time

import pytest


def test_fizzbuzz(load_exercise):
    fizzbuzz = load_exercise("ex01_fizzbuzz").fizzbuzz
    result = fizzbuzz(15)
    assert result[:5] == ["1", "2", "Fizz", "4", "Buzz"]
    assert result[-1] == "FizzBuzz" and len(result) == 15
    assert fizzbuzz(0) == []
    assert fizzbuzz(4, ((2, "A"), (4, "B"))) == ["1", "A", "3", "AB"]
    assert fizzbuzz(3, ()) == ["1", "2", "3"]
    with pytest.raises(ValueError):
        fizzbuzz(-1)
    with pytest.raises(ValueError):
        fizzbuzz(5, ((0, "Z"),))


def test_primes(load_exercise):
    primes_up_to = load_exercise("ex02_sieve").primes_up_to
    assert primes_up_to(10) == [2, 3, 5, 7]
    assert primes_up_to(2) == [2]
    assert primes_up_to(1) == [] and primes_up_to(-5) == []
    assert primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    start = time.perf_counter()
    big = primes_up_to(100_000)
    assert time.perf_counter() - start < 1.0
    assert len(big) == 9592


def test_window_max(load_exercise):
    window_max = load_exercise("ex03_window_max").window_max
    assert window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert window_max([4, 2], 1) == [4, 2]
    assert window_max([4, 2], 2) == [4]
    assert window_max([4, 2], 3) == []
    assert window_max([], 2) == []
    assert window_max([5, 5, 5], 2) == [5, 5]
    with pytest.raises(ValueError):
        window_max([1], 0)


def test_window_max_matches_naive(load_exercise):
    window_max = load_exercise("ex03_window_max").window_max
    values = [(i * 7919) % 101 for i in range(300)]
    for k in (1, 2, 5, 17, 300):
        expected = [max(values[i:i + k])
                    for i in range(len(values) - k + 1)]
        assert window_max(values, k) == expected


def test_rle(load_exercise):
    module = load_exercise("ex04_rle")
    assert module.rle_encode("aaabcc") == [("a", 3), ("b", 1), ("c", 2)]
    assert module.rle_encode("") == []
    assert module.rle_encode("abab") == [("a", 1), ("b", 1),
                                         ("a", 1), ("b", 1)]
    assert module.rle_decode([("a", 3), ("b", 1)]) == "aaab"
    assert module.rle_decode([]) == ""
    text = "wwwwbbbwwxyzzz"
    assert module.rle_decode(module.rle_encode(text)) == text


def test_my_batched(load_exercise):
    my_batched = load_exercise("ex05_batched_pairwise").my_batched
    assert list(my_batched("ABCDEFG", 3)) == list(
        itertools.batched("ABCDEFG", 3))
    assert list(my_batched([], 2)) == []
    assert list(my_batched(iter(range(4)), 2)) == [(0, 1), (2, 3)]
    assert list(my_batched(range(6), 3, strict=True)) == [
        (0, 1, 2), (3, 4, 5)]
    with pytest.raises(ValueError):
        list(my_batched(range(7), 3, strict=True))
    with pytest.raises(ValueError):
        list(my_batched([1], 0))


def test_my_pairwise(load_exercise):
    my_pairwise = load_exercise("ex05_batched_pairwise").my_pairwise
    assert list(my_pairwise([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
    assert list(my_pairwise([1])) == []
    assert list(my_pairwise([])) == []
    assert list(my_pairwise(iter("abc"))) == [("a", "b"), ("b", "c")]
    assert list(my_pairwise(range(50))) == list(
        itertools.pairwise(range(50)))


def test_first_duplicate(load_exercise):
    first_duplicate = load_exercise("ex06_first_duplicate").first_duplicate
    assert first_duplicate([2, 1, 3, 1, 2]) == (1, 3)
    assert first_duplicate([1, 2, 3]) is None
    assert first_duplicate([]) is None
    assert first_duplicate("abcdb") == ("b", 4)
    assert first_duplicate(iter([7, 7])) == (7, 1)
    assert first_duplicate([None, None]) == (None, 1)
