"""Exercício 2: verificar que as famílias de uma fábrica abstrata são COMPATÍVEIS (mesmos produtos, mesmas assinaturas)."""
import inspect


def check_families(families: dict[str, dict]) -> list[str]:
    """``families`` é ``{nome_da_familia: {nome_do_produto: função}}``. A PRIMEIRA família (na ordem do dict) é a referência. Devolve a lista de
    problemas (vazia se tudo combina), em ordem de família e, dentro dela, de produto (ordem alfabética):

    * ``f"{familia}: falta {produto!r}"`` para um produto da referência que a família não tem;
    * ``f"{familia}: produto extra {produto!r}"`` para um produto que a referência não tem;
    * ``f"{familia}: {produto!r} tem parâmetros ({a}, {b}), esperado ({x}, {y})"`` quando os NOMES dos parâmetros (``inspect.signature``, na
      ordem) diferem dos da referência;
    * ``f"{familia}: {produto!r} não é chamável"`` quando o valor não é um callable (e nesse caso não compare os parâmetros).
    Para cada família, primeiro os faltantes e extras (nessa ordem, alfabéticos) e depois os de parâmetros e não-chamáveis, alfabéticos.
    Dict vazio: ``[]``. Uma família só: ``[]`` (ela é a referência)."""
    raise NotImplementedError
