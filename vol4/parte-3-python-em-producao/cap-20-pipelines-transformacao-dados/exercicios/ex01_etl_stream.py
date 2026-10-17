"""Exercício 1: um ETL em FLUXO (geradores): validar, rejeitar com motivo e nunca carregar tudo na memória."""
from collections.abc import Iterable, Iterator


class Rejected(Exception):
    """Uma linha que não presta (o motivo é a mensagem)."""


def parse_line(line: str) -> dict:
    """Converte UMA linha de CSV ``event_id,user_id,product,qty,price`` (5 campos, sem cabeçalho, separados por vírgula) em um dict
    ``{"event_id": int, "user_id": int, "product": str, "qty": int, "price": float, "total": float}`` (``total = qty * price``
    arredondado a 2 casas). Linhas ruins levantam ``Rejected`` com UM destes motivos, nesta ordem de verificação:

    * ``"colunas"``: não tem exatamente 5 campos;
    * ``"user_id vazio"``: o segundo campo (sem espaços nas pontas) é vazio;
    * ``"número inválido"``: ``event_id``, ``user_id`` ou ``qty`` não são inteiros, ou ``price`` não é número;
    * ``"quantidade não positiva"``: ``qty <= 0``;
    * ``"preço negativo"``: ``price < 0``.
    ``product`` é cortado nas pontas (``strip``) e posto em minúsculas."""
    raise NotImplementedError


def transform(lines: Iterable[str], rejects: list, skip_header: bool = True) -> Iterator[dict]:
    """GERADOR: lê ``lines`` (qualquer iterável de textos, p. ex. um arquivo aberto) UMA linha de cada vez e produz os registros
    BONS, na ordem. As ruins vão para ``rejects`` como ``(numero_da_linha, motivo)``, em que o número conta a partir de 1 sobre as
    linhas recebidas (o cabeçalho é a linha 1). Linhas em branco (só espaços/quebra de linha) são IGNORADAS em silêncio e NÃO vão
    para ``rejects``. Um ``event_id`` repetido (já visto antes em uma linha BOA) é rejeitado com o motivo ``"event_id duplicado"``.
    Com ``skip_header=True``, a primeira linha é descartada (não é lida como dado). NUNCA guarde as linhas em uma lista."""
    raise NotImplementedError


def batched(items: Iterable, size: int) -> Iterator[list]:
    """GERADOR: agrupa ``items`` em listas de até ``size`` elementos (a última pode ser menor), sem consumir mais que o necessário
    de ``items`` para produzir cada lote. ``size < 1``: ``ValueError`` (ao PRIMEIRO ``next``, ou imediatamente: escolha, mas
    levante antes de produzir qualquer lote)."""
    raise NotImplementedError


def summarize(good_count: int, rejects: list) -> dict:
    """``{"loaded": good_count, "rejected": len(rejects), "reasons": {motivo: quantidade}}`` com os motivos em ordem decrescente de
    quantidade (empate: ordem alfabética do motivo)."""
    raise NotImplementedError
