"""Gabarito do exercício 6."""
import math


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def approx_equal(actual, expected, rel=1e-6, abs_tol=1e-12, nan_ok=False):
    if isinstance(expected, bool) or isinstance(actual, bool):
        return isinstance(actual, bool) and isinstance(expected, bool) and actual == expected
    if _is_number(expected):
        if not _is_number(actual):
            return False
        if math.isnan(expected) or math.isnan(actual):
            return nan_ok and math.isnan(expected) and math.isnan(actual)
        if actual == expected:
            return True
        if math.isinf(actual) or math.isinf(expected):
            return False
        return abs(actual - expected) <= max(rel * abs(expected), abs_tol)
    if isinstance(expected, (list, tuple)):
        return (isinstance(actual, (list, tuple)) and len(actual) == len(expected)
                and all(approx_equal(a, e, rel, abs_tol, nan_ok) for a, e in zip(actual, expected)))
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and actual.keys() == expected.keys()
                and all(approx_equal(actual[k], expected[k], rel, abs_tol, nan_ok) for k in expected))
    if _is_number(actual) or isinstance(actual, (list, tuple, dict)):
        return False
    return actual == expected
