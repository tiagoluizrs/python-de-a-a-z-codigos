"""Exercício 4: repetir transações que o servidor derrubou (deadlock e timeout de trava)."""
import time  # noqa: F401

RETRYABLE = (1213, 1205)          # 1213 = Deadlock found; 1205 = Lock wait timeout exceeded


def run_with_retry(func, attempts=3, delay=0.05, sleep=time.sleep):
    """Chama ``func()`` (uma transação completa, que devolve um valor) até ``attempts`` vezes.

    * repete SOMENTE se levantar ``pymysql.err.OperationalError`` cujo ``args[0]`` esteja em
      ``RETRYABLE``; qualquer outra exceção sobe na hora;
    * espera ``sleep(delay * 2**falhas_anteriores)`` entre tentativas;
    * esgotadas, re-levante a última; ``attempts < 1`` levanta ``ValueError``;
    * devolve o valor da primeira tentativa que funcionar."""
    raise NotImplementedError


def transfer(conn, source_id, target_id, amount):
    """Tabela ``account(id INT PRIMARY KEY, balance INT NOT NULL)``. Em UMA transação,
    trave as duas contas com ``SELECT ... WHERE id IN (...) ORDER BY id FOR UPDATE``, confira o
    saldo e mova ``amount``; confirme. Contas iguais, valor ``<= 0``, conta inexistente ou
    saldo insuficiente levantam ``ValueError`` (com ``rollback``). ``conn`` tem autocommit
    DESLIGADO e ``DictCursor``."""
    raise NotImplementedError
