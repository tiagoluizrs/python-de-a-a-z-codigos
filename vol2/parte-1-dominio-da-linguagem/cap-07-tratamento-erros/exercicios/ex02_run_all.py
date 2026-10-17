"""Exercício 2: executar tudo e reportar todas as falhas juntas."""


def run_all(tasks):
    """Execute cada callable de ``tasks`` e devolva a lista dos resultados.

    Se UMA OU MAIS tarefas levantarem ``Exception``, execute todas mesmo assim
    e, no fim, levante ``ExceptionGroup("n tarefas falharam", erros)`` com as
    exceções na ordem das tarefas (n = quantidade de falhas).
    Em caso de sucesso total, devolva só os resultados.
    """
    raise NotImplementedError


def count_by_type(group):
    """Conte as exceções FOLHA de um grupo (inclusive grupos aninhados).

    Devolva um dict ``{"ValueError": 2, ...}`` com o nome da classe de cada
    folha. Dica: ``isinstance(item, BaseExceptionGroup)`` e recursão.
    """
    raise NotImplementedError
