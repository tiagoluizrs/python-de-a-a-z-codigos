"""Exercício 3: uma facade simples por padrão, com opções avançadas e uma saída de emergência para o subsistema."""


class Fetcher:
    """``Fetcher(transport, *, timeout=5.0, headers=None, retries=0)``: facade sobre um ``transport`` (qualquer objeto com
    ``transport.request(url, timeout, headers) -> str``, que pode levantar ``ConnectionError``).

    * ``get(url, *, timeout=None, headers=None, retries=None)``: ``timeout``, ``headers`` e ``retries`` omitidos (``None``) usam os padrões da instância;
      ``headers`` passados são MESCLADOS por cima dos padrões (não substituem tudo; chaves repetidas vencem as passadas); ``retries`` é o número de
      TENTATIVAS EXTRAS depois da primeira, só para ``ConnectionError`` (qualquer outra exceção sobe na hora); esgotadas as tentativas, a última
      ``ConnectionError`` sobe. Devolve o texto da resposta;
    * ``timeout`` precisa ser ``> 0`` e ``retries >= 0``: senão ``ValueError`` (``"timeout inválido"`` / ``"retries inválido"``), tanto no construtor quanto
      no ``get``;
    * ``with_options(**mudancas)``: devolve um NOVO ``Fetcher`` com ``timeout``, ``headers`` e/ou ``retries`` trocados (a instância original não muda;
      ``headers`` dados aqui são MESCLADOS com os atuais); opção desconhecida: ``TypeError(f"opção desconhecida: {nome}")``;
    * ``transport`` é um atributo PÚBLICO (a saída de emergência);
    * ``stats``: ``{"calls": n, "retries": n}`` com o total de chamadas a ``get`` e de tentativas extras realmente feitas, nesta instância."""

    def __init__(self, transport, *, timeout: float = 5.0, headers: dict | None = None, retries: int = 0):
        raise NotImplementedError

    def get(self, url: str, *, timeout=None, headers=None, retries=None) -> str:
        raise NotImplementedError

    def with_options(self, **changes) -> "Fetcher":
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        raise NotImplementedError
