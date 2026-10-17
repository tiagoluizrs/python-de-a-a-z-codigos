"""Exercício 1: políticas de espera (backoff) como FUNÇÕES ``attempt -> segundos`` e um ``retry`` que as recebe. ``attempt`` começa em 1."""


def fixed(seconds: float):
    """Espera sempre ``seconds``. ``seconds < 0``: ``ValueError("espera negativa")`` (na criação)."""
    raise NotImplementedError


def linear(step: float):
    """Espera ``step * attempt``. ``step < 0``: ``ValueError("espera negativa")``."""
    raise NotImplementedError


def exponential(base: float = 1.0, factor: float = 2.0, cap: float | None = None):
    """Espera ``base * factor ** (attempt - 1)``, limitada a ``cap`` se ``cap`` não for ``None``. ``base < 0``, ``factor < 1`` ou ``cap < 0``: ``ValueError``
    (``"parâmetros inválidos"``)."""
    raise NotImplementedError


def with_jitter(strategy, rng):
    """Uma estratégia que ENVOLVE outra: ``strategy(attempt) * rng()`` (``rng`` devolve um número entre 0 e 1; injetável para os testes)."""
    raise NotImplementedError


def total_wait(strategy, attempts: int) -> float:
    """A soma das esperas das ``attempts - 1`` pausas entre ``attempts`` tentativas (``strategy(1) + ... + strategy(attempts - 1)``). ``attempts < 1``: ``ValueError``."""
    raise NotImplementedError


def retry(action, strategy, attempts: int, sleep, retry_on=(ConnectionError,)):
    """Chama ``action()`` até ``attempts`` vezes. Se levantar uma exceção de ``retry_on``, chama ``sleep(strategy(tentativa))`` e tenta de novo, exceto na ÚLTIMA
    tentativa, em que a exceção sobe (sem ``sleep``). Outras exceções sobem na hora. Devolve o resultado da primeira tentativa que funcionar.
    ``attempts < 1``: ``ValueError("attempts deve ser >= 1")``."""
    raise NotImplementedError


POLICIES: dict = {}     # preencha com "fixed", "linear" e "exponential"


def make_policy(name: str, *args, **kwargs):
    """A política pelo nome (``POLICIES[name](*args, **kwargs)``). Desconhecida: ``ValueError(f"política desconhecida: {name!r}; disponíveis: a, b, c")`` (alfabético)."""
    raise NotImplementedError
