"""Exercício 4: a corrida entre corrotinas."""


async def first_of(*factories):
    """Cada ``factory`` é um callable sem argumentos que devolve uma corrotina.
    Executa todos ao mesmo tempo e devolve o resultado do PRIMEIRO que terminar
    COM SUCESSO.

    * as demais são CANCELADAS e ESPERADAS (sua limpeza acabou quando ``first_of``
      retorna);
    * falhas são ignoradas enquanto algum puder vencer; se TODAS falharem,
      levante ``ExceptionGroup("todas falharam", [erros...])``;
    * sem ``factories`` levanta ``ValueError``."""
    raise NotImplementedError
