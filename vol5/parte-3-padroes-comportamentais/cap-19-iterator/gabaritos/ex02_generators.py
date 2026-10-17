"""Gabarito do exercício 2."""
import heapq
import io
from collections import deque
from itertools import islice


def chunks(iterable, size):
    if size < 1:
        raise ValueError("size deve ser >= 1")

    def generator():
        it = iter(iterable)
        while block := list(islice(it, size)):
            yield block

    return generator()


def sliding_window(iterable, n):
    if n < 1:
        raise ValueError("n deve ser >= 1")

    def generator():
        window = deque(maxlen=n)
        for item in iterable:
            window.append(item)
            if len(window) == n:
                yield tuple(window)

    return generator()


def unique_everseen(iterable, key=None):
    seen = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item


def merge_sorted(*iterables):
    heap = []
    for index, iterable in enumerate(iterables):
        it = iter(iterable)
        for first in it:
            heap.append((first, index, it))
            break
    heapq.heapify(heap)
    while heap:
        value, index, it = heap[0]
        yield value
        for nxt in it:
            heapq.heapreplace(heap, (nxt, index, it))
            break
        else:
            heapq.heappop(heap)


def flatten(nested, levels=None):
    stack = [(iter(nested), 0)]
    while stack:
        it, depth = stack[-1]
        for item in it:
            if isinstance(item, (list, tuple)) and (levels is None or depth < levels):
                stack.append((iter(item), depth + 1))
                break
            yield item
        else:
            stack.pop()


def read_blocks(stream, size):
    if size < 1:
        raise ValueError("size deve ser >= 1")
    sentinel = "" if isinstance(stream, io.TextIOBase) else b""
    return iter(lambda: stream.read(size), sentinel)
