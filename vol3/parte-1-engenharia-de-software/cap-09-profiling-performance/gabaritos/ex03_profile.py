"""Gabarito do exercício 3."""
import cProfile
import pstats


def _run(func, args, kwargs):
    profile = cProfile.Profile()
    result = profile.runcall(func, *args, **kwargs)
    return result, pstats.Stats(profile).stats


def profile_function(func, *args, top=5, **kwargs):
    result, stats = _run(func, args, kwargs)
    rows = [(key[2], value[1], value[2]) for key, value in stats.items()]
    rows.sort(key=lambda row: row[2], reverse=True)
    return result, rows[:top]


def call_counts(func, *args, **kwargs):
    _, stats = _run(func, args, kwargs)
    return {key[2]: value[1] for key, value in stats.items() if not key[0].startswith("~")}
