"""Gabarito do exercício 4."""


def recommend(cpu_bound, items, async_library=False, shared_state=False):
    if items < 0:
        raise ValueError("items negativo")
    if items <= 1:
        return "none"
    if cpu_bound:
        return "free-threading" if shared_state else "processes"
    return "asyncio" if async_library and items > 500 else "threads"


def explain(cpu_bound, items, async_library=False, shared_state=False):
    model = recommend(cpu_bound, items, async_library, shared_state)
    if model == "none":
        return "none: nada a paralelizar"
    return f"{model}: carga de {'CPU' if cpu_bound else 'E/S'} com {items} itens"
