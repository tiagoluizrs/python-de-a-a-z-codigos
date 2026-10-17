"""Exercício 4: novas tentativas em um executor."""
import time  # noqa: F401


def submit_with_retry(executor, func, *args, retries=3, retry_on=(Exception,), delay=0.0, sleep=time.sleep):
    """Executa ``func(*args)`` no ``executor`` e devolve o resultado, tentando de novo
    se levantar uma exceção de ``retry_on``.

    * no máximo ``1 + retries`` tentativas (cada uma uma NOVA submissão);
    * entre tentativas, ``sleep(delay * 2**numero_da_tentativa_que_falhou)``
      (``delay=0`` não dorme; a primeira falha é a tentativa 0);
    * se esgotar, re-levanta a ÚLTIMA exceção;
    * exceções fora de ``retry_on`` são re-levantadas na hora, sem repetir;
    * ``retries < 0`` levanta ``ValueError``."""
    raise NotImplementedError
