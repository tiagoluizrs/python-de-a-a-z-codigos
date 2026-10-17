"""Exercício 4: medir o que uma facade tira do cliente: quantas operações do subsistema cada função conhece."""
import ast
import textwrap


def coupling(source: str) -> dict[str, list[str]]:
    """Para cada função (``def`` e ``async def``, inclusive métodos, que aparecem como ``"Classe.metodo"``; funções aninhadas NÃO entram) de ``source``
    (use ``textwrap.dedent``), devolve a lista ORDENADA e sem repetições do que ela "conhece" do subsistema:

    * as chamadas da forma ``objeto.metodo(...)`` em que ``objeto`` é um nome simples (``ast.Name``), como ``"objeto.metodo"`` (``self.x.y()``,
      ``a().b()`` e ``a[0].b()`` NÃO contam: só o nome simples antes do ponto);
    * os nomes de exceção tratados em ``except Nome:`` ou ``except (A, B):`` (cada ``Nome``);
    O resultado tem uma chave por função, na ordem em que aparecem no código (as chaves dos métodos usam o nome da classe)."""
    raise NotImplementedError


def facade_gain(before: str, after: str, function: str) -> int:
    """Quantas operações do subsistema a função ``function`` deixou de conhecer entre as duas versões do código: ``len(coupling(before)[function]) -
    len(coupling(after)[function])`` (pode ser negativo). Função que não existe em uma das versões: ``KeyError(function)``."""
    raise NotImplementedError


def most_coupled(source: str, top: int = 3) -> list[tuple[str, int]]:
    """As ``top`` funções com mais operações conhecidas, como ``(nome, quantidade)``, da maior para a menor (empate: nome em ordem alfabética);
    funções com 0 não entram na lista."""
    raise NotImplementedError
