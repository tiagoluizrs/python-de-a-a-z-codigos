"""Exercício 1: enxergar a diferença entre cópia rasa e profunda: quais contêineres os dois objetos compartilham?"""


def shared_mutables(a, b, _path: str = "") -> list[str]:
    """Compara as estruturas ``a`` e ``b`` (compostas de ``dict``, ``list``, ``set`` e ``tuple``, em qualquer profundidade) e devolve os CAMINHOS
    onde elas guardam o MESMO objeto mutável (``is``), em ordem alfabética.

    * só ``dict``, ``list`` e ``set`` contam como "mutáveis" (números, textos e tuplas não entram na lista, mesmo que sejam o mesmo objeto);
    * o caminho de um ``dict`` usa o ponto (``"limits.max"``), o de uma ``list`` ou ``tuple`` usa o índice (``"tags[0]"``); a raiz é ``""``
      (se ``a is b`` e são mutáveis, o caminho é ``"."``);
    * quando dois objetos mutáveis são o MESMO, registre o caminho e NÃO desça neles (tudo que há dentro é obviamente compartilhado);
    * quando são objetos diferentes, desça: ``dict`` pelas chaves comuns, ``list`` e ``tuple`` pelos índices comuns;
    * tipos diferentes ou valores atômicos diferentes: nada a registrar. Ciclos não precisam ser tratados."""
    raise NotImplementedError


def is_independent(a, b) -> bool:
    """Verdadeiro se ``a`` e ``b`` NÃO compartilham nenhum contêiner mutável (``shared_mutables`` vazio)."""
    raise NotImplementedError


def make_grid(rows: int, cols: int, value=0) -> list[list]:
    """Uma grade ``rows`` x ``cols`` de ``value`` com linhas INDEPENDENTES (o oposto de ``[[v] * cols] * rows``). ``rows`` ou ``cols`` negativos:
    ``ValueError("dimensões negativas")``."""
    raise NotImplementedError
