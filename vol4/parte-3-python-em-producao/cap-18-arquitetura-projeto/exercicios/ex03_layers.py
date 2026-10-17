"""Exercício 3: fiscalizar a REGRA DE DEPENDÊNCIA (as camadas internas não importam as externas) lendo o código com ``ast``."""
import ast


def imports_of(module: str, source: str, package: str) -> set[str]:
    """Os módulos INTERNOS que ``source`` importa (só os que começam com ``package``). ``module`` é o nome do próprio módulo
    (ex.: ``"loja.services.checkout"``), usado para resolver imports RELATIVOS.

    * ``import loja.domain.order`` -> ``"loja.domain.order"``;
    * ``from loja.domain import order, money`` -> ``"loja.domain"``, ``"loja.domain.order"`` e ``"loja.domain.money"``;
    * ``from loja.domain.order import Order`` -> ``"loja.domain.order"`` e ``"loja.domain.order.Order"``;
    * imports relativos (``from . import x`` / ``from ..domain import y``) resolvem a partir do pacote de ``module`` (``level 1``
      = o pacote do módulo; ``level 2`` = o pai dele): ``from ..domain import y`` em ``loja.services.checkout`` é
      ``"loja.domain"`` e ``"loja.domain.y"``;
    * qualquer coisa que não comece com ``package`` (biblioteca padrão, terceiros) é ignorada; ``from x import *`` conta só o módulo;
    * o próprio módulo não conta como dependência dele mesmo."""
    raise NotImplementedError


def layer_violations(sources: dict[str, str], layers: list[str], package: str) -> list[tuple[str, str]]:
    """``sources`` mapeia nome de módulo -> código-fonte. ``layers`` lista as camadas da MAIS INTERNA para a mais externa
    (ex.: ``["domain", "services", "adapters"]``); a camada de um módulo é o segundo componente do nome
    (``loja.domain.order`` -> ``"domain"``); módulos fora das camadas (ex.: ``loja.bootstrap``) não têm camada e podem importar
    qualquer coisa.

    Devolve a lista de pares ``(importador, importado)`` em que um módulo de uma camada IMPORTA um módulo de uma camada MAIS
    EXTERNA (violação), sem repetir pares, em ordem alfabética. Imports entre módulos da MESMA camada ou de uma camada mais
    externa para uma mais interna são permitidos; só módulos reais de ``sources`` contam (``loja.domain.order.Order`` resolve para
    ``loja.domain.order``; um nome que não é módulo de ``sources`` é ignorado)."""
    raise NotImplementedError


def find_cycles(sources: dict[str, str], package: str) -> list[list[str]]:
    """Ciclos de importação entre módulos de ``sources``: cada ciclo é uma lista de módulos que começa no MENOR nome do
    ciclo e termina repetindo-o (``["a", "b", "a"]``). Cada ciclo uma vez só, em ordem alfabética pelo primeiro módulo. Sem
    ciclos: ``[]``. Importar um pacote (``loja.domain``) conta como importar ``loja.domain.__init__`` só se ele estiver em
    ``sources``."""
    raise NotImplementedError
