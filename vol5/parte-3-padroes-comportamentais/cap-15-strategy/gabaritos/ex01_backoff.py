"""Gabarito do exercício 1."""


def fixed(seconds):
    if seconds < 0:
        raise ValueError("espera negativa")
    return lambda attempt: seconds


def linear(step):
    if step < 0:
        raise ValueError("espera negativa")
    return lambda attempt: step * attempt


def exponential(base=1.0, factor=2.0, cap=None):
    if base < 0 or factor < 1 or (cap is not None and cap < 0):
        raise ValueError("parâmetros inválidos")

    def delay(attempt):
        value = base * factor ** (attempt - 1)
        return value if cap is None else min(value, cap)

    return delay


def with_jitter(strategy, rng):
    return lambda attempt: strategy(attempt) * rng()


def total_wait(strategy, attempts):
    if attempts < 1:
        raise ValueError("attempts deve ser >= 1")
    return sum(strategy(i) for i in range(1, attempts))


def retry(action, strategy, attempts, sleep, retry_on=(ConnectionError,)):
    if attempts < 1:
        raise ValueError("attempts deve ser >= 1")
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except retry_on:
            if attempt == attempts:
                raise
            sleep(strategy(attempt))


POLICIES = {"fixed": fixed, "linear": linear, "exponential": exponential}


def make_policy(name, *args, **kwargs):
    try:
        factory = POLICIES[name]
    except KeyError:
        raise ValueError(f"política desconhecida: {name!r}; disponíveis: {', '.join(sorted(POLICIES))}") from None
    return factory(*args, **kwargs)
