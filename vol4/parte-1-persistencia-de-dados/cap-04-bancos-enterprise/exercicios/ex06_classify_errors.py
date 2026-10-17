"""Exercício 6: classificar erros de banco (e decidir o que repetir)."""

CATEGORIES = ("duplicate", "deadlock", "timeout", "connection", "other")


def classify_error(dialect, code):
    """Classifica o ``code`` do erro do ``dialect`` em uma de ``CATEGORIES``:

    * ``postgresql`` (SQLSTATE, texto): ``23505`` duplicate; ``40P01`` e ``40001`` deadlock;
      ``57014`` e ``55P03`` timeout; qualquer um que comece com ``08`` connection;
    * ``mysql`` e ``mariadb`` (inteiro): ``1062`` duplicate; ``1213`` e ``1020`` deadlock;
      ``1205`` timeout; ``2002``, ``2003``, ``2006``, ``2013`` connection;
    * ``oracle`` (número do ORA-): ``1`` duplicate; ``60`` deadlock; ``30006`` e ``54`` timeout;
      ``3113``, ``3114``, ``12170``, ``12541`` connection;
    * ``mssql`` (número do erro): ``2627`` e ``2601`` duplicate; ``1205`` deadlock; ``-2`` timeout;
      ``10053``, ``10054``, ``10060`` connection;
    * ``sqlite`` (``str`` com o nome da exceção ou mensagem): contém ``UNIQUE`` duplicate; contém
      ``locked`` timeout; senão other;
    * qualquer outro código: ``other``; dialeto desconhecido levanta ``ValueError``."""
    raise NotImplementedError


def is_retryable(category):
    """``True`` para ``deadlock``, ``timeout`` e ``connection`` (repetir a transação inteira
    pode resolver); ``False`` para ``duplicate`` e ``other`` (repetir o mesmo comando falha
    de novo). Categoria desconhecida levanta ``ValueError``."""
    raise NotImplementedError
