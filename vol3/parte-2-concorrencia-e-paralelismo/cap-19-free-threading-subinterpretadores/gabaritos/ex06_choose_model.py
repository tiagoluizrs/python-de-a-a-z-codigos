"""Gabarito do exercício 6."""


def choose_model(*, cpu_bound, many_connections=False, shared_data=False, free_threaded=False, uses_pure_python=True):
    if not cpu_bound:
        return "asyncio" if many_connections else "threads"
    if free_threaded:
        return "free-threaded threads"
    return "interpreters" if uses_pure_python else "processes"
