"""Exercício 1: novas tentativas com espera exponencial e jitter (sem dormir de verdade: ``sleep`` e ``rng`` são injetados)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 4                      # tentativas TOTAIS (a primeira conta)
    base: float = 0.5                          # espera antes da 2ª tentativa (segundos), sem jitter
    factor: float = 2.0
    cap: float = 30.0                          # teto de uma espera
    jitter: str = "full"                       # "none" | "full" | "equal"
    retry_on: tuple = (ConnectionError, TimeoutError)


class RetriesExhausted(Exception):
    def __init__(self, attempts: int, last_error: Exception):
        self.attempts, self.last_error = attempts, last_error
        super().__init__(f"desistindo depois de {attempts} tentativas: {last_error!r}")


def delay_ceiling(policy: RetryPolicy, failures: int) -> float:
    """O TETO da espera depois de ``failures`` falhas (``failures >= 1``): ``min(base * factor ** (failures - 1), cap)``."""
    raise NotImplementedError


def delay(policy: RetryPolicy, failures: int, rng) -> float:
    """A espera sorteada depois de ``failures`` falhas, conforme ``policy.jitter``:

    * ``"none"``: exatamente o teto;
    * ``"full"``: ``rng.uniform(0, teto)``;
    * ``"equal"``: ``teto / 2 + rng.uniform(0, teto / 2)``;
    * outro valor: ``ValueError``.
    ``rng`` é um ``random.Random`` (ou parecido, com ``uniform``)."""
    raise NotImplementedError


def retry_call(fn, policy: RetryPolicy, sleep, rng):
    """Chama ``fn()`` até dar certo, no máximo ``policy.max_attempts`` vezes, e devolve o resultado.

    * só repete se a exceção for uma instância de ``policy.retry_on``; qualquer OUTRA exceção sobe na hora, sem repetir;
    * entre uma tentativa e a seguinte, chame ``sleep(delay(policy, falhas_até_agora, rng))`` (NÃO durma depois da última);
    * quando as tentativas acabarem, levante ``RetriesExhausted(tentativas, último_erro)``."""
    raise NotImplementedError


def total_wait_ceiling(policy: RetryPolicy) -> float:
    """O pior caso de espera acumulada entre todas as tentativas (soma dos tetos de ``delay_ceiling`` para
    ``1 .. max_attempts - 1`` falhas)."""
    raise NotImplementedError
