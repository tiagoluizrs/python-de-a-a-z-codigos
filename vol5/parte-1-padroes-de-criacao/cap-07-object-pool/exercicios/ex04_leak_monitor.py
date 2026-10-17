"""Exercício 4: detectar vazamentos de pool: quem pegou um objeto e NÃO devolveu? (o relógio é injetado, como no Capítulo 7 do Volume 3)"""


class LeaseMonitor:
    """``LeaseMonitor(clock)``: ``clock`` é um callable sem argumentos que devolve segundos (um ``float``).

    * ``acquired(label)``: registra um empréstimo em ``clock()`` e devolve um TOKEN (inteiro: 1, 2, 3... na ordem dos empréstimos); ``label`` é um
      texto que identifica quem pegou (um nome de função, de requisição...);
    * ``released(token)``: encerra o empréstimo; token desconhecido ou já devolvido: ``ValueError("token desconhecido")``;
    * ``active``: quantos empréstimos estão abertos;
    * ``overdue(max_age)``: lista ``(label, idade)`` dos empréstimos abertos com idade MAIOR que ``max_age`` (``clock() - início``), do mais velho
      para o mais novo (empate: ordem alfabética do ``label``); ``max_age < 0``: ``ValueError``;
    * ``report(max_age)``: um texto com uma linha por atrasado, ``f"{label}: {idade:.1f}s"``, separadas por ``\\n`` na mesma ordem; sem atrasados:
      ``"sem vazamentos"``."""

    def __init__(self, clock):
        raise NotImplementedError

    def acquired(self, label: str) -> int:
        raise NotImplementedError

    def released(self, token: int) -> None:
        raise NotImplementedError

    @property
    def active(self) -> int:
        raise NotImplementedError

    def overdue(self, max_age: float) -> list[tuple[str, float]]:
        raise NotImplementedError

    def report(self, max_age: float) -> str:
        raise NotImplementedError
