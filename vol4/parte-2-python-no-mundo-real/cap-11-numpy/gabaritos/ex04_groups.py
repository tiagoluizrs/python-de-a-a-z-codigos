"""Gabarito do exercício 4."""
import numpy as np


def group_sum(keys, values, n_groups):
    return np.bincount(np.asarray(keys), weights=np.asarray(values, dtype=np.float64), minlength=n_groups)


def group_mean(keys, values, n_groups):
    sums = group_sum(keys, values, n_groups)
    counts = np.bincount(np.asarray(keys), minlength=n_groups)
    return np.divide(sums, counts, out=np.full(n_groups, np.nan), where=counts > 0)


def group_max(keys, values, n_groups):
    out = np.full(n_groups, -np.inf)
    np.maximum.at(out, np.asarray(keys), np.asarray(values, dtype=np.float64))
    return out


def top_k_per_group(keys, values, n_groups, k):
    keys = np.asarray(keys)
    values = np.asarray(values, dtype=np.float64)
    return [np.sort(values[keys == g])[::-1][:k] for g in range(n_groups)]
