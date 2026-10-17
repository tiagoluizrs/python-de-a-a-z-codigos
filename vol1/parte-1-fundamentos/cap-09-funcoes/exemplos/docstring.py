"""Docstrings e help()."""


def clamp(value: float, low: float, high: float) -> float:
    """Limite ``value`` ao intervalo [``low``, ``high``].

    Args:
        value: número a limitar.
        low: limite inferior.
        high: limite superior.

    Returns:
        ``low`` se ``value < low``, ``high`` se ``value > high``,
        senão o próprio ``value``.

    Raises:
        ValueError: se ``low > high``.
    """
    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(value, high))


print(clamp.__doc__.splitlines()[0])
help(clamp)
print(clamp(15, 0, 10), clamp(-3, 0, 10), clamp(5, 0, 10))
