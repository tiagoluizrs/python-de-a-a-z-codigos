"""Gabarito do exercício 3."""


def describe_chain(error):
    chain = []
    seen = set()
    while error is not None and id(error) not in seen:   # evita ciclos
        seen.add(id(error))
        chain.append(f"{type(error).__name__}: {error}")
        if error.__cause__ is not None:
            error = error.__cause__
        elif not error.__suppress_context__:
            error = error.__context__
        else:
            error = None
    return chain
