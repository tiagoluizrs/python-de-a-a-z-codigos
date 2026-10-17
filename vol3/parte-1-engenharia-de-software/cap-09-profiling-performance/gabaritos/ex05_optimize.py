"""Gabarito do exercício 5."""
from collections import Counter


def unique_naive(items):
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def unique_fast(items):
    return list(dict.fromkeys(items))


def common_naive(a, b):
    return [x for x in a if x in b]


def common_fast(a, b):
    lookup = set(b)
    return [x for x in a if x in lookup]


def pair_count_naive(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def pair_count_fast(nums, target):
    seen, count = Counter(), 0
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count


def frequencies_naive(words):
    return {w: words.count(w) for w in words}


def frequencies_fast(words):
    return dict(Counter(words))


def fib_naive(n):
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


def fib_fast(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
