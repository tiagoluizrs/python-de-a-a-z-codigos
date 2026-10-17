"""Exercício 4: tentar de novo com educação (sem rede e sem dormir de verdade: ``get`` e ``sleep`` são injetados)."""


class GaveUp(Exception):
    """Todas as tentativas falharam."""


def get_with_backoff(get, url: str, sleep, max_attempts: int = 4, base: float = 0.5, cap: float = 8.0):
    """``get(url)`` devolve ``(status, headers, body)``; ``headers`` é um dict com chaves em minúsculas.

    * status ``200`` a ``399``, e ``400`` a ``499`` EXCETO ``429``: devolva ``body`` na hora (erro do cliente não
      melhora tentando de novo; nesse caso para 4xx, devolva também ``body``: quem chama decide);
    * ``429`` e ``500`` a ``599``: espere e tente de novo, até ``max_attempts`` tentativas no total;
    * quanto esperar: se houver o cabeçalho ``retry-after`` com um número de segundos, espere EXATAMENTE isso
      (mesmo que seja maior que ``cap``); senão, ``min(base * 2 ** n, cap)`` com ``n = 0, 1, 2...`` (``n`` conta as
      falhas já ocorridas);
    * chame ``sleep(segundos)`` entre as tentativas, e NÃO depois da última;
    * se a última tentativa também falhar, levante ``GaveUp`` com a mensagem
      ``"desistindo de <url> após <max_attempts> tentativas (último status: <status>)"``."""
    raise NotImplementedError
