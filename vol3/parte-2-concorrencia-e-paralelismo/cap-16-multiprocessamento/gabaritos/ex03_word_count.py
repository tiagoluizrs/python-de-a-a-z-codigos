"""Gabarito do exercício 3."""
import collections
import multiprocessing as mp

import tasks


def merge_counts(counters):
    total = collections.Counter()
    for counter in counters:
        total.update(counter)
    return total


def parallel_word_count(texts, processes=2):
    texts = list(texts)
    if not texts:
        return collections.Counter()
    with mp.Pool(processes) as pool:
        partials = pool.map(tasks.count_words, texts)
    return merge_counts(partials)
