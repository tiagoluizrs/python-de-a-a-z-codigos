"""Exercício 5: coletar o que der dentro de um prazo."""


async def collect_with_timeout(factories, timeout):
    """Executa as corrotinas (``factories``: callables sem argumentos) ao mesmo tempo
    e espera no máximo ``timeout`` segundos NO TOTAL. Devolve
    ``(resultados, atrasadas)``:

    * ``resultados``: dicionário ``{índice: valor}`` das que terminaram a tempo;
    * ``atrasadas``: lista ORDENADA dos índices das que não terminaram; elas são
      canceladas e esperadas (nada fica rodando);
    * se alguma que terminou a tempo levantou exceção, cancele as demais e a
      re-levante;
    * ``timeout <= 0`` leva todas a ``atrasadas`` (e as cancela)."""
    raise NotImplementedError
