"""Gabarito do exercício 1."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 4
    base: float = 0.5
    factor: float = 2.0
    cap: float = 30.0
    jitter: str = "full"
    retry_on: tuple = (ConnectionError, TimeoutError)


class RetriesExhausted(Exception):
    def __init__(self, attempts, last_error):
        self.attempts, self.last_error = attempts, last_error
        super().__init__(f"desistindo depois de {attempts} tentativas: {last_error!r}")


def delay_ceiling(policy, failures):
    return min(policy.base * policy.factor ** (failures - 1), policy.cap)


def delay(policy, failures, rng):
    ceiling = delay_ceiling(policy, failures)
    if policy.jitter == "none":
        return ceiling
    if policy.jitter == "full":
        return rng.uniform(0, ceiling)
    if policy.jitter == "equal":
        return ceiling / 2 + rng.uniform(0, ceiling / 2)
    raise ValueError(f"jitter desconhecido: {policy.jitter!r}")


def retry_call(fn, policy, sleep, rng):
    last = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except policy.retry_on as error:
            last = error
            if attempt == policy.max_attempts:
                break
            sleep(delay(policy, attempt, rng))
    raise RetriesExhausted(policy.max_attempts, last)


def total_wait_ceiling(policy):
    return sum(delay_ceiling(policy, k) for k in range(1, policy.max_attempts))
