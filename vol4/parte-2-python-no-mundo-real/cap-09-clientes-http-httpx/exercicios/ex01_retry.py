"""Exercício 1: novas tentativas com Retry-After, jitter injetável e só para métodos seguros."""
import time  # noqa: F401

IDEMPOTENT = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}


def request_with_retry(client, method, url, *, retries=3, backoff=0.1, retry_statuses=(429, 502, 503, 504), sleep=time.sleep, **kwargs):
    """Envia ``client.request(method, url, **kwargs)`` e repete quando necessário.

    * até ``1 + retries`` tentativas; só repete se o método for IDEMPOTENTE (``IDEMPOTENT``) E
      (o status estiver em ``retry_statuses`` OU levantar ``httpx.ConnectError``/``httpx.ReadTimeout``);
    * espera antes de repetir: se a resposta tiver ``Retry-After`` (segundos, inteiro ou decimal), esse valor;
      senão ``backoff * 2 ** (tentativa_que_falhou - 1)`` (a 1ª falha usa ``backoff``);
    * chama ``sleep(espera)`` (injetável nos testes); nunca espera depois da ÚLTIMA tentativa;
    * esgotadas as tentativas: se a última coisa foi uma RESPOSTA com status de retry, devolva-a;
      se foi uma exceção, re-levante-a;
    * método não idempotente (POST, PATCH) nunca é repetido: devolve a primeira resposta (ou deixa a exceção subir);
    * ``retries < 0`` levanta ``ValueError``."""
    raise NotImplementedError
