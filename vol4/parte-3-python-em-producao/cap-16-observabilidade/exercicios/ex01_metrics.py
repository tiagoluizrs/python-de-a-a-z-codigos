"""Exercício 1: um miniprometheus_client (para entender o que a biblioteca faz por baixo)."""


class Counter:
    """Um contador que só sobe, com rótulos."""

    def __init__(self, name: str, label_names: tuple[str, ...] = ()):
        raise NotImplementedError

    def inc(self, amount: float = 1, **labels) -> None:
        """Soma ``amount`` à série dos ``labels``. ``amount`` negativo: ``ValueError``. Rótulos diferentes dos
        declarados (faltando ou sobrando): ``ValueError``."""
        raise NotImplementedError

    def value(self, **labels) -> float:
        """O valor atual da série (``0.0`` se ainda não existe). Mesma validação dos rótulos."""
        raise NotImplementedError


class Histogram:
    """Um histograma com buckets cumulativos (como o do Prometheus)."""

    def __init__(self, name: str, buckets: list[float], label_names: tuple[str, ...] = ()):
        """``buckets`` são os limites superiores, em ordem crescente (``ValueError`` se não estiverem ordenados ou
        forem vazios); existe sempre um último bucket ``+Inf``."""
        raise NotImplementedError

    def observe(self, value: float, **labels) -> None:
        raise NotImplementedError

    def counts(self, **labels) -> list[int]:
        """Contagens CUMULATIVAS por bucket, incluindo o ``+Inf`` no fim (``len(buckets) + 1`` itens). Uma observação
        de valor ``v`` entra em todo bucket com limite ``>= v``. Série inexistente: tudo ``0``."""
        raise NotImplementedError

    def quantile(self, q: float, **labels) -> float:
        """Estima o percentil ``q`` (``0 < q < 1``) como o ``histogram_quantile`` do Prometheus: acha o primeiro bucket
        cuja contagem cumulativa é ``>= q * total`` e interpola linearmente entre o limite anterior (``0`` para o
        primeiro) e o limite do bucket. Se cair no bucket ``+Inf``, devolva o maior limite finito. Sem observações:
        ``float('nan')``."""
        raise NotImplementedError


def render(metrics: list) -> str:
    """O texto de exposição das métricas, na ordem dada, terminado por ``\\n``:

    * contador: ``# TYPE <nome> counter`` e uma linha ``<nome>_total{a="1",b="2"} <valor>`` por série (rótulos na ordem
      declarada; séries ordenadas pelos valores dos rótulos; sem rótulos: sem chaves). Valor sempre ``float`` (``3.0``);
    * histograma: ``# TYPE <nome> histogram`` e, por série, uma linha ``<nome>_bucket{<rótulos>,le="<limite>"} <contagem>``
      para cada bucket (o último com ``le="+Inf"``; o limite impresso com ``repr(float(limite))``, ex.: ``0.5``),
      depois ``<nome>_sum{...}`` e ``<nome>_count{...}``."""
    raise NotImplementedError
